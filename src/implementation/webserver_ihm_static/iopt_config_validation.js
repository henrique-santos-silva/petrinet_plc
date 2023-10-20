function is_valid_expression(expression,extra_tokens){
    const valid_tokens = [...extra_tokens,'(',')','|','&','^','!','true','false'];
    s1 = expression.split(' ').join("");
    tmp_tokens = [];
    tmp_tokens_bool_substitution = []
    back_pointer = 0;
    front_pointer = 0;
    while (front_pointer <= s1.length) {
        let substring = s1.substring(back_pointer,front_pointer);
        if (valid_tokens.includes(substring)) {
            tmp_tokens.push(substring)
            back_pointer = front_pointer;

            if (extra_tokens.includes(substring)){
                tmp_tokens_bool_substitution.push("true")
            }else{
                tmp_tokens_bool_substitution.push(substring)
            }

        }else{
            front_pointer = front_pointer + 1;
        }
    }
    s2 = tmp_tokens.join("")
    const contains_only_valid_tokens = s1 == s2
    const final_expression = tmp_tokens.join(" ")
    const proxy_expression_for_validation = tmp_tokens_bool_substitution.join(" ")
    
    if (contains_only_valid_tokens){
        try{
            eval(!(!(eval(proxy_expression_for_validation)))) 

            return [true,final_expression]
        }
        catch (e){
            console.log("Invalid boolean expression")
            console.log(e); // Logs the error            
            return [false,""]
        }
    }else{
        return [false,""]
    }
}

function  is_form_valid(IOPT_dictionary){
    const transition_signal_enabling_condition_Container = document.getElementById("transition_signal_enabling_condition_container");
    const output_activation_condition_Container = document.getElementById("output_activation_condition_container");
    const timed_transition_timer_Container = document.getElementById("timed_transition_timer_container");
    
    const transition_signal_enabling_condition = {}
    const marking_to_output_expressions = {}
    const timed_condition_timer = {}

    // Loop through the children
    extra_tokens = ["i0","i1","i2","i3","i4","i5","i6","i7",]
    for (let i = 0; i < transition_signal_enabling_condition_Container.children.length; i++) {
        const child = transition_signal_enabling_condition_Container.children[i];
        const label = child.querySelector(".form-label");
        const input = child.querySelector(".transition_signal_enabling_condition_textfield");
        const [valid_expression_bool,new_string] = is_valid_expression(input.value,extra_tokens)
        if (!(valid_expression_bool && new_string != "")){
            return false
        }else{
            transition_signal_enabling_condition[label.textContent] = input.value
        }
    }


    extra_tokens = IOPT_dictionary["places"].map(function(place){return place["id"]})
    for (let i = 0; i < output_activation_condition_Container.children.length; i++) {
        const child = output_activation_condition_Container.children[i];
        const input = child.querySelector(".output_activation_condition_textfield");
        const label = child.querySelector(".form-label");
        const [valid_expression_bool,new_string] = is_valid_expression(input.value,extra_tokens)
        if (!(valid_expression_bool && new_string != "")){
            return false
        }else{
            marking_to_output_expressions[label.textContent] = input.value
        }
    }

    for (let i = 0; i < timed_transition_timer_Container.children.length; i++) {
        const child = timed_transition_timer_Container.children[i];
        const input = child.querySelector(".timed_transition_timer_textfield");
        const label = child.querySelector(".form-label");

        if (input.value < 0){
            return false
        }
        else{
            timed_condition_timer[label.textContent] = input.value
        }
    }

    // valid
    IOPT_dictionary["marking_to_output_expressions"] = marking_to_output_expressions
    for (const transition of IOPT_dictionary["instantaneous_transitions"]){
        transition["signal_enabling_expression"] = transition_signal_enabling_condition[transition["id"]]
    }
    for (const transition of IOPT_dictionary["timed_transitions"]){
        transition["signal_enabling_expression"] = transition_signal_enabling_condition[transition["id"]]
        transition["timer_sec"] = parseFloat(timed_condition_timer[transition["id"]])
    }
    return true
}