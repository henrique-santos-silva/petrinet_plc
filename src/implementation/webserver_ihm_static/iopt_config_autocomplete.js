var activeInputField = null;


function get_autocomplete_suggestions( // return list[str]
    input_text, //str
    extra_tokens //list[str]
){
    const autocomplete_words = [...extra_tokens,'true','false'];
    let current_word   = input_text.slice(input_text.lastIndexOf(" ") + 1);
    let suggestions = autocomplete_words.filter(autocomplete_word => autocomplete_word.toLowerCase().startsWith(current_word.toLowerCase()))

    return suggestions
}

function update_autocomplete_content( // returns None
    suggestions //list[str]
){
    let listGroup = $('#autocomplete_content .list-group');
    listGroup.empty(); // Clear any existing list items
    suggestions.forEach(function(suggestions) {
        console.log("loop")
        listGroup.append(
            '<a href="#" class="list-group-item list-group-item-action">' + suggestions + '</a>'
        );
    });
}

function navigate_autocomplete_content_list(direction) {
    let listItems = $('.popover-body .list-group-item-action');
    
    // var listItems = $('#autocomplete_content .list-group .list-group-item-action');

    let activeItem = listItems.filter('.active');
    let currentIndex = listItems.index(activeItem);
    console.log(currentIndex)
    let nextItem = direction === 'down' ? listItems.eq((currentIndex + 1)%listItems.length) : listItems.eq((currentIndex - 1)%listItems.length);

    if (nextItem.length) {
        console.log("updating")
        activeItem.removeClass('active');
        nextItem.addClass('active');
    }
}


function accept_autocomplete_suggestion(current_text, accepted_word) {
    // Separa o texto atual em palavras
    let words = current_text.split(" ");
    // Remove a última palavra
    words.pop();
    // Adiciona a palavra aceita ao final do array
    words.push(accepted_word);
    // Junta o array em uma string, com espaços entre as palavras
    return words.join(" ") + " ";
}


function generate_text_after_suggestion_accepted(
    current_text,//str
    accepted_word//str
){
    let words = current_text.split(" ");
    // Remove a última palavra
    words.pop();
    // Adiciona a palavra aceita ao final do array
    words.push(accepted_word);
    // Junta o array em uma string, com espaços entre as palavras
    return words.join(" ");
}

function apply_popover_to_inputs(
    inputs,//list[str]
    places//list[str]

){
    
    $('.transition_signal_enabling_condition_textfield, .output_activation_condition_textfield').popover({
        trigger: 'input',
        html: true,
        placement: 'right',
        content: function() {
            return $('#autocomplete_content').html();
        }
    }).on('focus input', function() {
        activeInputField = $(this);
        // var _this = this;
        if ($(this).hasClass('transition_signal_enabling_condition_textfield')) {
            extra_tokens = inputs;
        } else if ($(this).hasClass('output_activation_condition_textfield')) {
            extra_tokens = places;
        }
        let suggestions = get_autocomplete_suggestions($(this).val(),extra_tokens)
        update_autocomplete_content(suggestions)
        $('#autocomplete_content .list-group .list-group-item-action').first().addClass('active');
        $(this).popover('show');
    }).on('blur', function() {
        $(this).popover('hide');
    }).on('keydown', function(e) {
        if (e.keyCode === 40) { // down arrow
            navigate_autocomplete_content_list('down');
        } else if (e.keyCode === 38) { // up arrow
            navigate_autocomplete_content_list('up', $(this).next('.popover').find('.popover-body'));
        }else if( e.keyCode === 13){ // enter
            var listItems = $('.popover-body .list-group-item-action');
            var activeItem = listItems.filter('.active');
            current_text = $(this).val()
            new_text = generate_text_after_suggestion_accepted(current_text =current_text,accepted_word=activeItem.text())
            $(this).val(new_text)
            $(this).trigger("change")
            console.log(new_text)
        } 

    }).on('change', function() {
        let extra_tokens = null;
        if ($(this).hasClass('transition_signal_enabling_condition_textfield')) {
            extra_tokens = inputs;
        } else if ($(this).hasClass('output_activation_condition_textfield')) {
            extra_tokens = places;
        }


        let valid_expression_bool;
        let new_string; 
        [valid_expression_bool, new_string] = is_valid_expression($(this).val(), extra_tokens);
        if (valid_expression_bool && new_string != ""){
            $(this).removeClass('border border-danger');
            $(this).val(new_string);
        } else {
            $(this).addClass('border border-danger');
        }
    });

    $(document).on('click', '.list-group-item-action', function(e) {
        e.preventDefault();
        let text = $(this).text();
        let newText = generate_text_after_suggestion_accepted(activeInputField.val(), text);
        activeInputField.val(newText).popover('hide');
        activeInputField.trigger("change");
    });
}


