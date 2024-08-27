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
        'and':'&','or': '|','not': '!','xor': '^',
        'AND':'&','OR': '|','NOT': '!','XOR': '^'  
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


function validadeIOPT(IOPT_dictionary) {
    
    const errors = {};

    // verifica se os digital outputs são os esperados
    const marking_to_output_expressions = IOPT_dictionary["marking_to_output_expressions"] || {};

    const expectedOutputsSet = new Set();
    for (let i = 0; i <= 15; i++) {
        const value = `DO${i}`;
        expectedOutputsSet.add(value);
    }
    const actualOutputSet = new Set(Object.keys(marking_to_output_expressions))

    const missingDigitalOutputs = [...expectedOutputsSet.difference(actualOutputSet)];
    const exceedingDigitalOutputs = [...actualOutputSet.difference(expectedOutputsSet)];

    if (missingDigitalOutputs.length > 0){
        errors['missingDigitalOutputs'] = missingDigitalOutputs;
    }
    if (exceedingDigitalOutputs.length > 0){
        errors['exceedingDigitalOutputs'] = exceedingDigitalOutputs;
    }

    // Validação das condições de ativação de saída
    let outputActivationExpressionErrors = {};
    for (const output_name in marking_to_output_expressions) {
        const expression = marking_to_output_expressions[output_name];
        const [valid_expression_bool, new_string] = is_valid_expression(
            expression,
            IOPT_dictionary["places"].map(p => p.id) // Considera os lugares como tokens válidos para saídas
        );

        if (!valid_expression_bool) {
            outputActivationExpressionErrors[output_name] = expression;
        }else{
            // Atualiza a expressão válida no dicionário de marcações para saídas
            marking_to_output_expressions[output_name] = new_string;
        }
    }
    if (Object.keys(outputActivationExpressionErrors).length > 0){
        errors['outputActivationExpressionErrors'] = outputActivationExpressionErrors
    }

    const transitionSignalEnablingExpresionErrors = {}
    const transitionList = [...IOPT_dictionary["instantaneous_transitions"],...IOPT_dictionary["timed_transitions"]] 
    transitionList.forEach(t => {
        const transitionName = t.id;
        const expression = t.signal_enabling_expression;
        const [valid_expression_bool, new_string] = is_valid_expression(
            expression,
            [...Array(8).keys()].map(i => `DI${i}`) // Considera DI0 a DI7 como tokens válidos para transições
        );

        if (!valid_expression_bool){
            transitionSignalEnablingExpresionErrors[transitionName] = expression;
        }else{
            // Update expression
            // Atualiza a transição com a expressão válida
            const transition = 
                IOPT_dictionary["instantaneous_transitions"].find(t => t.id === transitionName) ||
                IOPT_dictionary["timed_transitions"].find(t => t.id === transitionName);

            if (transition) {
                transition["signal_enabling_expression"] = new_string;
            }
        }
    });
    if (Object.keys(transitionSignalEnablingExpresionErrors).length > 0){
        errors['transitionSignalEnablingExpresionErrors'] = transitionSignalEnablingExpresionErrors;
    }

    // check places and transition names
    const invalidPlaceNameErrors = []
    placeNames = IOPT_dictionary['places'].map(p=>p.id);
    placeNames.forEach(pname=>{
        if (!isValidPythonVariableName(pname) || pname[0].toLowerCase() !== 'p'){
            invalidPlaceNameErrors.push(pname);
        }
    })
    if (invalidPlaceNameErrors.length > 0){
        errors['invalidPlaceNameErrors'] = invalidPlaceNameErrors;
    }

    const invalidTransitionNameErrors = []
    transitionList.map(t => t.id).forEach( tname => {
        if (!isValidPythonVariableName(tname)){
            invalidTransitionNameErrors.push(tname);
        }
    })
    if (invalidTransitionNameErrors.length > 0){
        errors['invalidTransitionNameErrors'] = invalidTransitionNameErrors;
    }

    return errors;
}


function isValidPythonVariableName(name) {
    // Verifique se o nome é uma palavra reservada em Python
    const pythonKeywords = new Set([
        "False", "None", "True", "and", "as", "assert", "async", "await", "break", 
        "class", "continue", "def", "del", "elif", "else", "except", "finally", 
        "for", "from", "global", "if", "import", "in", "is", "lambda", "nonlocal", 
        "not", "or", "pass", "raise", "return", "try", "while", "with", "yield"
    ]);

    if (pythonKeywords.has(name)) {
        return false;
    }

    // Verifique se o nome segue as regras de nomenclatura
    const validPattern = /^[A-Za-z_][A-Za-z0-9_]*$/;

    return validPattern.test(name);
}