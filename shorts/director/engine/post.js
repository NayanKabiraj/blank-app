// Full-screen passes: scene-to-scene transitions (all 11 registered types in one shader) and the final film look.
export const TRANSITIONS = ['particle-dissolve', 'camera-fly-through', 'geometry-wipe', 'zoom-tunnel', 'whip-pan', 'object-occlusion', 'grid-collapse', 'light-sweep', 'depth-push', 'match-motion', 'fade-through-black'];

const VERT = 'varying vec2 vUv; void main(){ vUv = uv; gl_Position = projectionMatrix*modelViewMatrix*vec4(position,1.); }';

export const MixShader = {
  uniforms: { tDiffuse: { value: null }, tA: { value: null }, tB: { value: null }, p: { value: 0 }, type: { value: 0 }, aspect: { value: 1 }, seed: { value: 0 }, dir: { value: [1, 0] }, glow: { value: [0, 0.85, 1] } },
  vertexShader: VERT,
  fragmentShader: `
    varying vec2 vUv; uniform sampler2D tA, tB; uniform float p, aspect, seed; uniform int type; uniform vec2 dir; uniform vec3 glow;
    float hash(vec2 s){ return fract(sin(dot(s, vec2(12.9898,78.233)) + seed)*43758.5453); }
    float vnoise(vec2 x){ vec2 i = floor(x), f = fract(x); f = f*f*(3.-2.*f); return mix(mix(hash(i), hash(i+vec2(1,0)), f.x), mix(hash(i+vec2(0,1)), hash(i+vec2(1,1)), f.x), f.y); }
    vec4 S(sampler2D t, vec2 uv){ return texture2D(t, clamp(uv, 0., 1.)); }
    vec4 radial(sampler2D t, vec2 uv, float k){ vec4 c = vec4(0.); for(int i=0;i<8;i++){ float s = float(i)/7.; c += S(t, 0.5 + (uv-0.5)*(1.-k*s)); } return c/8.; }
    vec4 lin(sampler2D t, vec2 uv, vec2 d){ vec4 c = vec4(0.); for(int i=0;i<8;i++){ float s = float(i)/7. - 0.5; c += S(t, uv + d*s); } return c/8.; }
    void main(){
      vec2 uv = vUv, c = vec2(.5); float e = p*p*(3.-2.*p); vec4 col;
      vec2 ca = (uv-c)*vec2(aspect,1.);
      if (type == 0) { col = S(tA, uv); }
      else if (type == 1) { // particle-dissolve
        float n = vnoise(uv*vec2(aspect,1.)*14.)*0.65 + hash(floor(uv*vec2(aspect,1.)*110.))*0.35; float th = e*1.25 - 0.12;
        float m = step(n, th); float edge = smoothstep(th-0.07, th, n) * (1. - step(th, n));
        col = mix(S(tA, uv), S(tB, uv), m) + vec4(glow*2.2*edge, 0.);
      }
      else if (type == 2) { // camera-fly-through: dive into A, emerge from B
        float k = smoothstep(0.35, 0.65, p);
        vec4 a = radial(tA, uv, 0.55*e); vec4 a2 = S(tA, c + (uv-c)/(1.+e*2.4));
        vec4 b = S(tB, c + (uv-c)*(0.55+0.45*e)); vec4 br = radial(tB, uv, 0.4*(1.-e));
        col = mix(mix(a2, a, 0.5), mix(b, br, 0.5), k) + vec4(glow*0.5*sin(3.14159*p)*(1.-length(uv-c)), 0.);
      }
      else if (type == 3) { // geometry-wipe: diamond cells sweep across
        vec2 g = fract(uv*vec2(aspect,1.)*7.) - .5; float cell = (abs(g.x)+abs(g.y)); float s = (uv.x + uv.y*0.6)/1.6;
        float m = smoothstep(0., 0.12, e*1.5 - s - cell*0.35 + 0.0);
        float edge = (1.-abs(m*2.-1.)); col = mix(S(tA, uv), S(tB, uv), m) + vec4(glow*edge*0.6, 0.);
      }
      else if (type == 4) { // zoom-tunnel: swirl + zoom
        float r = length(ca); float ang = e*3.2*(1.-smoothstep(0.,1.1,r)); float cs = cos(ang), sn = sin(ang);
        vec2 q = vec2(cs*ca.x - sn*ca.y, sn*ca.x + cs*ca.y); vec2 u2 = c + q/vec2(aspect,1.);
        vec4 a = radial(tA, c + (u2-c)/(1.+e*2.2), 0.4*e), b = radial(tB, c + (u2-c)*(0.45+0.55*e), 0.3*(1.-e));
        col = mix(a, b, smoothstep(0.4, 0.6, p));
      }
      else if (type == 5) { // whip-pan
        float amt = sin(3.14159*p); vec2 sh = dir*e; vec2 ua = uv + sh, ub = uv + dir*(e-1.);
        vec4 a = lin(tA, ua, dir*0.18*amt), b = lin(tB, ub, dir*0.18*amt);
        bool inA = ua.x >= 0. && ua.x <= 1. && ua.y >= 0. && ua.y <= 1.; col = inA ? a : b;
      }
      else if (type == 6) { // object-occlusion: a disc grows from the centre and reveals the next scene
        float r = e*1.55, d = length(ca); float m = smoothstep(r, r-0.015, d); float rim = smoothstep(0.05, 0., abs(d-r));
        col = mix(S(tA, uv)*(1.-0.5*smoothstep(r, r+0.5, d)*e), S(tB, uv), m) + vec4(glow*rim*1.6, 0.);
      }
      else if (type == 7) { // grid-collapse: cells shrink away at random moments
        vec2 gv = uv*vec2(aspect,1.)*9.; vec2 id = floor(gv), f = fract(gv)-.5; float h = hash(id);
        float m = smoothstep(h*0.55, h*0.55+0.35, e*1.35); float sz = 0.5*(1.-m);
        col = max(abs(f.x), abs(f.y)) < sz ? S(tA, uv) : S(tB, uv);
      }
      else if (type == 8) { // light-sweep
        float d = uv.x + uv.y*0.35 - (e*1.7 - 0.3); float m = step(d, 0.); float bar = exp(-abs(d)*16.);
        col = mix(S(tB, uv), S(tA, uv), step(0., d)) ; col.rgb += vec3(1.,.95,.85)*bar*1.6 + glow*bar*0.6;
      }
      else if (type == 9) { // depth-push
        vec4 a = S(tA, c + (uv-c)/(1.+e*0.45)), b = S(tB, c + (uv-c)*(0.8+0.2*e)); col = mix(a, b, smoothstep(0.15, 0.85, p));
      }
      else if (type == 10) { // match-motion: carry the movement across the cut
        vec4 a = lin(tA, uv - dir*e*0.3, dir*0.05*sin(3.14159*p)), b = lin(tB, uv + dir*(1.-e)*0.3, dir*0.05*sin(3.14159*p)); col = mix(a, b, smoothstep(0.25, 0.75, p));
      }
      else { // fade-through-black
        col = p < 0.5 ? S(tA, uv)*(1.-p*2.) : S(tB, uv)*(p*2.-1.);
      }
      gl_FragColor = vec4(col.rgb, 1.);
    }`,
};

export const FxShader = {
  uniforms: { tDiffuse: { value: null }, time: { value: 0 }, grain: { value: 0.08 }, vig: { value: 0.2 }, ca: { value: 0.015 }, glitch: { value: 0 }, seed: { value: 0 }, sat: { value: 1 }, gain: { value: 1 } },
  vertexShader: VERT,
  fragmentShader: `
    varying vec2 vUv; uniform sampler2D tDiffuse; uniform float time, grain, vig, ca, glitch, seed, sat, gain;
    float hash(vec2 s){ return fract(sin(dot(s, vec2(12.9898,78.233)) + seed)*43758.5453); }
    void main(){
      vec2 uv = vUv;
      if (glitch > 0.001) { float band = floor(uv.y*28.); float h = hash(vec2(band, floor(time*14.))); if (h > 0.8) uv.x += (hash(vec2(band, 3.)) - 0.5)*glitch*0.7; }
      vec2 d = (uv - .5); float k = ca*dot(d,d)*2. + glitch*0.02;
      float r = texture2D(tDiffuse, uv + d*k).r, g = texture2D(tDiffuse, uv).g, b = texture2D(tDiffuse, uv - d*k).b;
      vec3 col = vec3(r,g,b);
      float v = 1. - vig*smoothstep(0.35, 0.95, length(d)*1.25); col *= v;
      col += (hash(uv*vec2(1920.,1080.) + floor(time*24.)) - .5)*grain*0.35;
      float l = dot(col, vec3(0.299, 0.587, 0.114)); col = mix(vec3(l), col, sat) * gain;
      gl_FragColor = vec4(col, 1.);
    }`,
};
