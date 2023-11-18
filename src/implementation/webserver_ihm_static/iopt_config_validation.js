function is_valid_expression( //--> list[str]
    expression, // str
    extra_tokens // list[str]
){
    expression = expression.replaceAll(" ","");
    if (expression === ""){
        return [false,""]
    }
    // let expression_lower = expression.toLowerCase();
    
    let extra_tokens_lower = extra_tokens.map(token=>token.toLowerCase());

    const basic_tokens = ['(',')','|','&','^','!','true','false'];
    const valid_tokens = [...extra_tokens,...basic_tokens];
    let p0=0,p1=0;
    const tokens = [];
    const tokens_bool_substitution = []; //tokens, with all variables changed to true. It will be used as a proxy for validation
    let token_tmp = null;

    while (p0 <= p1 && p1 <= expression.length) {
        let substring = expression.substring(p0,p1);
        let substring_lower = substring.toLowerCase()
        if (basic_tokens.includes(substring_lower)){
            tokens.push(substring);
            tokens_bool_substitution.push(substring_lower);
            p0 = p1;
            continue;
        }else if ( (substring_lower.startsWith('di')||substring_lower.startsWith('p'))  && extra_tokens_lower.includes(substring_lower)){
            token_tmp = substring;
        }else if ( (substring_lower.startsWith('di')||substring_lower.startsWith('p')   && ! extra_tokens_lower.includes(substring_lower))){
            if (token_tmp !== null){
                tokens.push(token_tmp);
                tokens_bool_substitution.push('true');
                token_tmp = null;
                p0 = p1= p1-1;
                continue;
            }
        }

        p1 += 1;
    }

    if (token_tmp !== null){
        tokens.push(token_tmp);
        tokens_bool_substitution.push('true');
    }

    if (tokens.join("") !== expression){
        // return tokens;
        return [false,""];
    }
    const final_expression = tokens.join(" ") + " ";
    const proxy_expression_for_validation = tokens_bool_substitution.join(" ");
    try{
        eval(!(!(eval(proxy_expression_for_validation)))) 
        return [true,final_expression]
    }
    catch (e){
        console.log("Invalid boolean expression")
        console.log(e); // Logs the error            
        return [false,""]
    }
}

function  is_form_valid(IOPT_dictionary){
    const transition_signal_enabling_condition_Container = document.getElementById("transition_signal_enabling_condition_container");
    const output_activation_condition_Container = document.getElementById("output_activation_condition_container");
    const timed_transition_timer_Container = document.getElementById("timed_transition_timer_container");
    
    const transition_signal_enabling_condition = {};
    const marking_to_output_expressions = {};
    const timed_condition_timer = {};

    // Loop through the children
    extra_tokens = [...Array(8).keys()].map(i => `DI${i}`)
    for (const row of transition_signal_enabling_condition_Container.children){
        const label = row.querySelector(".form-label");
        const input = row.querySelector(".transition_signal_enabling_condition_textfield");
        const [valid_expression_bool,new_string] = is_valid_expression(input.value,extra_tokens)
        if (!(valid_expression_bool && new_string != "")){
            return false
        }else{
            transition_signal_enabling_condition[label.textContent] = input.value;
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