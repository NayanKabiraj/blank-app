# Storyboard: sample_topic_001 (hi, cinematic)

## s1 - 0.0s to 4.0s - hook
- Narration: इस मुड़ी हुई छड़ी को सीधा और ज़ोर से फेंको, फिर भी यह तुम्हारे पास वापस आ जाती है। आखिर क्यों?
- Camera: slow_zoom_in (focus: hook_subject)
- Elements: svg_illustration:hook_subject (progressive_stroke_draw), label:headline (pop_in)
- Transition out: sketch_reveal

## s2 - 4.0s to 11.0s - explainer_diagram
- Narration: बूमरैंग की हर भुजा बिल्कुल एक छोटे हवाई जहाज़ के पंख जैसी बनी होती है।
- Camera: static (focus: wing_shape)
- Elements: svg_illustration:wing_shape (progressive_stroke_draw), arrow:pointer (draw_from_start)
- Transition out: crossfade

## s3 - 11.0s to 26.0s - explainer_diagram
- Narration: घूमते समय एक भुजा हवा में दूसरी से तेज़ चलती है, इसलिए वह ज़्यादा ज़ोर लगाती है - और एक तरफ ज़्यादा उठान बनाती है।
- Camera: pan_right (focus: lift_diagram)
- Elements: diagram:lift_diagram (progressive_stroke_draw), label:caption (fade_in)
- Transition out: crossfade

## s4 - 26.0s to 40.0s - comparison
- Narration: यह असमान धक्का ठीक वैसे काम करता है जैसे एक घूमते लट्टू को हल्का धक्का घुमा देता है - पूरा रास्ता एक घेरे में मुड़ जाता है।
- Camera: pan_left (focus: spin_turn)
- Elements: diagram:spin_a (progressive_stroke_draw), diagram:spin_b (progressive_stroke_draw)
- Transition out: line_draw

## s5 - 40.0s to 50.0s - explainer_diagram
- Narration: इसीलिए बिल्कुल सीधा फेंका गया बूमरैंग भी पूरा घूमकर तुम्हारे हाथ में वापस आ जाता है।
- Camera: static (focus: return_path)
- Elements: svg_illustration:return_path (draw_from_start)
- Transition out: crossfade

## s6 - 50.0s to 55.0s - takeaway
- Narration: एक मुड़ी छड़ी। एक घूमता करतब। हमेशा घर लौटती है।
- Camera: slow_zoom_in (focus: takeaway_text)
- Elements: label:takeaway_text (pop_in)
- Transition out: zoom
