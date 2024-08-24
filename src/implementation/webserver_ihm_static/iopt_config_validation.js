function is_valid_expression( //--> list[str]
    expression, // str
    extra_tokens // list[str]
) {
    expression = expression.replaceAll(" ", "");
    if (expression === "") {
        return [false, ""]
    }
    // let expression_lower = expression.toLowerCase();

    let extra_tokens_lower = extra_tokens.map(token => token.toLowerCase());

    basicTokensRegression = {
        'true':'true','false':'false','(':'(',')':')',
        '||':'|', '&&':'&', '^':'^', '!':'!', '~':'!',
        'and':'&','or': '|','not': '!','xor': '^'  
    }
    const basic_tokens = ['(', ')', '||', '&&', '^', '!', '~', 'true', 'false', 'and', 'or', 'not', 'xor'];
    const valid_tokens = [...extra_tokens, ...basic_tokens];
    let p0 = 0, p1 = 0;
    const tokens = [];
    const tokens_bool_substitution = []; //tokens, with all variables changed to true. It will be used as a proxy for validation
    let token_tmp = null;

    while (p0 <= p1 && p1 <= expression.length) {
        let substring = expression.substring(p0, p1);
        let substring_lower = substring.toLowerCase()
        if (basic_tokens.includes(substring_lower)) {
            tokens.push(substring);
            tokens_bool_substitution.push(basicTokensRegression[substring_lower]);
            p0 = p1;
            continue;
        } else if ((substring_lower.startsWith('di') || substring_lower.startsWith('p')) && extra_tokens_lower.includes(substring_lower)) {
            token_tmp = substring;
        } else if ((substring_lower.startsWith('di') || substring_lower.startsWith('p') && !extra_tokens_lower.includes(substring_lower))) {
            if (token_tmp !== null) {
                tokens.push(token_tmp);
                tokens_bool_substitution.push('true');
                token_tmp = null;
                p0 = p1 = p1 - 1;
                continue;
            }
        }

        p1 += 1;
    }

    if (token_tmp !== null) {
        tokens.push(token_tmp);
        tokens_bool_substitution.push('true');
    }

    if (tokens.join("") !== expression) {
        // return tokens;
        return [false, ""];
    }
    const final_expression = tokens
        .map(t => t in basicTokensRegression ?
                basicTokensRegression[t]:t
        ).join(" ") + " ";
    const proxy_expression_for_validation = tokens_bool_substitution.join(" ");
    try {
        eval(!(!(eval(proxy_expression_for_validation))))
        return [true, final_expression]
    }
    catch (e) {
        console.log("Invalid boolean expression")
        console.log(e); // Logs the error            
        return [false, ""]
    }
}

function is_form_valid(IOPT_dictionary) {
    const transition_signal_enabling_condition = IOPT_dictionary["transition_signal_enabling_condition"] || {};
    const marking_to_output_expressions = IOPT_dictionary["marking_to_output_expressions"] || {};

    // Validação das condições de habilitação de transição
    for (const transitionName in transition_signal_enabling_condition) {
        const expression = transition_signal_enabling_condition[transitionName];
        const [valid_expression_bool, new_string] = is_valid_expression(
            expression,
            [...Array(8).keys()].map(i => `DI${i}`) // Considera DI0 a DI7 como tokens válidos para transições
        );

        if (!valid_expression_bool) {
            return false;
        }

        // Atualiza a transição com a expressão válida
        const transition = IOPT_dictionary["instantaneous_transitions"].find(t => t.id === transitionName) ||
            IOPT_dictionary["timed_transitions"].find(t => t.id === transitionName);

        if (transition) {
            transition["signal_enabling_expression"] = new_string;
        }
    }

    // Validação das condições de ativação de saída
    for (const output_name in marking_to_output_expressions) {
        const expression = marking_to_output_expressions[output_name];
        const [valid_expression_bool, new_string] = is_valid_expression(
            expression,
            IOPT_dictionary["places"].map(p => p.id) // Considera os lugares como tokens válidos para saídas
        );

        if (!valid_expression_bool) {
            return false;
        }

        // Atualiza a expressão válida no dicionário de marcações para saídas
        marking_to_output_expressions[output_name] = new_string;
    }

    // Validação dos temporizadores de transição temporizada
    for (const transition of IOPT_dictionary["timed_transitions"]) {
        if (transition["timer_sec"] < 0) {
            return false;
        }
    }

    // Atualização final no IOPT_dictionary
    IOPT_dictionary["marking_to_output_expressions"] = marking_to_output_expressions;
    for (const transition of IOPT_dictionary["instantaneous_transitions"]) {
        transition["signal_enabling_expression"] = transition_signal_enabling_condition[transition["id"]];
    }
    for (const transition of IOPT_dictionary["timed_transitions"]) {
        transition["signal_enabling_expression"] = transition_signal_enabling_condition[transition["id"]];
        transition["timer_sec"] = parseFloat(transition["timer_sec"]);
    }

    return true;
}
