	$('#review-form').on('submit', function(event){
		event.preventDefault();
		function () {
			$.ajax({
				url : "/r/add/",
				type : "POST",
				data : { review : $('#id_review').val() },

				success : function(json) {
					$('#id_review').val('');
					console.log(json);
    				$("#book-reviews").prepend("<div><strong>"+json.username+"</strong> - <em> "+json.review+"</em></div>");

				},

				// handle a non-successful response
				error : function(xhr,errmsg,err) {
					$('#results').html("<div class='alert-box alert radius' data-alert>Oops! We have encountered an error: "+errmsg+
						" <a href='#' class='close'>&times;</a></div>"); // add the error to the dom
					console.log(xhr.status + ": " + xhr.responseText); // provide a bit more info about the error to the console
				}
			});
		};
	});