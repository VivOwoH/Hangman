
/* Submit letter */

$('#letter-form').submit(function(e) {
  var data = $("#letter-form").serialize()+"&formName=letter-form";
  console.log(data);
  
  /* Empty input */
  $('#letter-form input').val('');
  
  $.ajax({
    type: "POST",
    url: '',
    data: data,
    success: function(data) {
      /* Refresh if finished */
      if (data.finished) {
        location.reload();
      }
      else {
        /* Update current */
        $('#current').text(data.current);
        
        /* Update errors */
        $('#errors').html(
          ' (' + data.errors.length + '/6): ' +
          '<span class="text-danger spaced">' + data.errors + '</span>');
          
        /* Update drawing */
        updateDrawing(data.errors);
      }
    }
  });
  e.preventDefault();
});

function updateDrawing(errors) {
  $('#hangman-drawing').children().slice(0, errors.length).show();
}

$('#hint-form').submit(function(e) {
    var data = $("#hint-form").serialize()+"&formName=hint-form"

    $.ajax({
    type: "POST",
    url: '',
    data: data,
    success: function(data) {
      /* Refresh if finished */
      if (data.finished) {
        location.reload();
      }
      else {
        /* Update current */
        $('#current').text(data.current);

        /* Update errors */
        $('#errors').html(
          ' (' + data.errors.length + '/6): ' +
          '<span class="text-danger spaced">' + data.errors + '</span>');

        $('#hints').html("<span>Hint Counter: " + data.hint_max + "</span>");
           console.log(data.hint_max)

        /* Update drawing */
        updateDrawing(data.errors);
      }
    }
  });
  e.preventDefault();
});
