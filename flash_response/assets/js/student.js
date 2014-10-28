function RunningSesson(sessionCode) {
    this.sessionCode = sessionCode;

    this.checkForQuestions = function() {
        $.get('/student/check_question_availability/', {
            'session_code': this.sessionCode
        }, function(response) {
            if (response.question_available) {
                setTimeout(function() {
                    showQuestion(response);
                }, response.time_to_start);
            } else {
                // If there were no questions, check again in 2 seconds
                setTimeout(runningSession.checkForQuestions, 2000);
            }
        });
    };

    showQuestion = function(question) {
        $('#question-title').text(question.question_body);
        var question_option_template = $('#template-question-option').text();
        for (var i = question.question_options.length - 1; i >= 0; i--) {
            option = question.question_options[i];
            option_html = question_option_template;
            option_html = option_html.replace(/\[\# option_id \#\]/g, option.id);
            option_html = option_html.replace(/\[\# option_body \#\]/g, option.body);
            $('#question-option-container').append(option_html);
        };
        $('#wait-container').fadeOut(function() {
            $('#question-container').fadeIn();
            startQuestionTimer(question.run_time);
        });
    };

    startQuestionTimer = function(runTime) {
        var progressBarDelay = (runTime * 1000) / 100;
        var progressBarWidth = 0;
        var progressBarInterval = setInterval(function() {
            progressBarWidth++;
            $('#time-remaining-progress .progress-bar').width(progressBarWidth + '%');

            // Stop the progress bar once full
            if (progressBarWidth == 100) {
                clearInterval(progressBarInterval);
            }
        }, progressBarDelay);

        // Count down in seconds on the display
        var secondsRemaining = runTime;
        $('#seconds-remaining').text(secondsRemaining);
        var _this = this;
        var countdownInterval = setInterval(function() {
            secondsRemaining--;
            $('#seconds-remaining').text(secondsRemaining);

            if (secondsRemaining == 0) {
                clearInterval(countdownInterval);
                questionComplete(_this);
            }
        }, 1000);
    };

    questionComplete = function(_this) {
        uiToWaiting();
        runningSession.checkForQuestions();
    };

    uiToWaiting = function() {
        $('#time-remaining-progress .progress-bar').css('width', '0px');
        $('#question-container').fadeOut(function() {
            $('#wait-container').fadeIn();
        });
    };

    this.checkForQuestions();
}

var runningSession = new RunningSesson(sessionCode);