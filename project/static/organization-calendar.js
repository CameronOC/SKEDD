$(document).ready(function() {

    var create = true;

    /*
    *
    * Initialize Calendar
    *
    */
    var time = moment.duration('04:00:00');
    var firstHour = (moment(new Date()).local());
    firstHour.subtract(time);
    firstHour = firstHour.format("HH:00:00")

    $('#calendar').fullCalendar({
        header: {
            left: 'prev,next today',
            center: 'title',
            right: 'month,agendaWeek,agendaDay'
        },
        height: $(window).height()*0.67,
        defaultView: 'agendaWeek',
        scrollTime: firstHour,
        allDaySlot: false,
        editable: true,
        selectable: true,
        selectHelper: true,
        events: "/organization/" + orgid.toString() + "/shifts",
        eventRender: function(event, element) {
            element.find('.fc-title').after("<span class=\"assigned\">" + event.assigned_member + "</span>");
        },
        eventClick:  function(event, jsEvent, view) {
            create = false;
            $('#shift_start_time').val(event.start.toISOString());
            $('#shift_end_time').val(event.end.toISOString());
            $('#shift_id').val(event.id);
            $('#shiftSubmit').prop('disabled', true);
            $('#shiftDelete').show();

            $('#shift_position_id').val(event.position_id)
            updateUsersForPosition(event.position_id, event.assigned_member_id);

            console.log(event.description);
            $('#shift_description').val(event.description);

            $('#createMultipleShifts').hide();

            $('#shiftModal').modal('show');
        },
        select: function(start, end, allDay) {

            var newEvent = {
                start: start,
                end: end,
                id: 0,
            };
            create = true;
            $('#calendar').fullCalendar( 'renderEvent', newEvent , 'stick');
            $('#shift_start_time').val(start.toISOString());
            $('#shift_end_time').val(end.toISOString());
            $('#shift_id').val('0');
            $('#shiftSubmit').prop('disabled', true);
            $('#shiftDelete').hide();

            $('#createMultipleShifts').show();

            $('#shiftModal').modal('show');

        },
        eventResize: function(event, delta, revertFunc) {
            updateTime(event, delta, revertFunc);
        },
        eventDrop: function(event, delta, revertFunc) {
            updateTime(event, delta, revertFunc);
        },
    });


    if(calendar) {
      $(window).resize(function() {
        var calHeight = $(window).height()*0.67;
        $('#calendar').fullCalendar('option', 'height', calHeight);
      });
    };




    $('.modal').on('hidden.bs.modal', function(){
        $(this).find("input,textarea").val('').end();
        $('#shift_assigned_member_id').empty();
        $('#shift_position_id').val('0');
        $("#shift_repeat_list option:selected").prop("selected", false);
        $('#shift_repeating').prop('checked', false);
        $('#shift_repeat_list').hide();
    });

    /*
    *
    * Shifts Code
    *
    */

    function createSuccess() {
        $('#calendar').fullCalendar( 'removeEvents', 0);
        $('#calendar').fullCalendar( 'refetchEvents' );
        $('#shiftModal').modal('hide');
    }


    function updateSuccess(shift) {
        var tempId = parseInt($('#shift_id').val());

        var eventlist = $("#calendar").fullCalendar('clientEvents', tempId);

        event = eventlist[0];

        event.title = shift.position_title;
        event.description = shift.description;
        event.assigned_member = shift.assigned_member;
        event.assigned_member_id = shift.assigned_member_id;
        event.position_id = shift.position_id;
        event.start = shift.start;
        event.end = shift.end;
        event.id = shift.id;

        $('#calendar').fullCalendar('updateEvent', event);
        $('#shiftModal').modal('hide');
    }


    $('#shiftSubmit').on('click', function() {
        $('#shiftSubmit').prop('disabled', true);


        if (create == true) {
            url = "/organization/" + orgid.toString() + "/shift/create";
        } else {
            url = '/organization/' + orgid.toString() + '/shift/' + ($('#shift_id').val()).toString() + '/update';
        }

        $.ajax({
            headers: {
                'Accept': "application/json; charset=utf-8",
            },
            type: "POST",
            url: url,
            data: $("#shiftForm").serialize(), // serializes the form's elements.

            success: function(data)
            {

                if(data.status == "success"){

                    if (create) {
                        createSuccess();
                    } else {
                        updateSuccess(data.shift);
                    }

                }else if(data.status == "error"){
                    alert(JSON.stringify(data));
                    $('#shiftSubmit').prop('disabled', false);
                }
            }
        });



    });

    $('#shiftCancel').on('click', function() {
        if (create) {
            $('#calendar').fullCalendar( 'removeEvents', 0);
        }
        $('#shiftSubmit').prop('disabled', true);
        $('#shiftModal').modal('hide');
    });

    $('#shiftDelete').on('click', function() {

        var tempId = $('#shift_id').val();

        $('#shiftSubmit').prop('disabled', true);
        $('#shiftDelete').prop('disabled', true);
        url = '/organization/' + orgid.toString() + '/shift/' + (tempId).toString() + '/delete';

        $.ajax({
            headers: {
                'Accept': "application/json; charset=utf-8",
            },
            type: "DELETE",
            url: url,

            success: function(data)
            {

                if(data.status == "success"){

                    $('#calendar').fullCalendar( 'removeEvents', tempId);
                    $('#shiftModal').modal('hide');

                }else if(data.status == "error"){
                    alert('Unable to Delete Shift: ' + JSON.stringify(data));
                    $('#shiftSubmit').prop('disabled', false);

                }

                $('#shiftDelete').prop('disabled', false);
            }
        });


    });


    $('#shift_repeating').change(function() {
        $('#shift_repeat_list').toggle();
        $("#shift_repeat_list option:selected").prop("selected", false);
    });

    /*
    *
    * This function makes an ajax call to the server to get the members for a position
    * whenever a position is selected in the create shift modal
    * these members are then used as options to the assigned member select field
    *
    */
    $('#shift_position_id').change(function() {
        updateUsersForPosition($(this).val(), null);
    });

    /*
    *
    * Makes an ajax call to get users for a position
    *
    */
    function updateUsersForPosition(position, member_id) {

        url = "/organization/" + orgid.toString() + "/position/" + position.toString() + "/users";

        $.ajax({
            headers: {
                'Accept': "application/json; charset=utf-8",
            },
            type: "GET",
            url: url,

            success: function(data)
            {
                if(data.status == "success"){
                    $('#shift_assigned_member_id').empty()

                    var html = '<option class="generated" value="0">Unassigned</option>';
                    $('#shift_assigned_member_id').append(html);

                    for (var i = 0; i < data.members.length; i++) {
                        var current = data.members[i];
                        var html = '<option class="generated" value="' + (current.id).toString() + '">' +
                                    current.first_name + ' ' + current.last_name + '</option>'
                        $('#shift_assigned_member_id').append(html);
                    }

                    if (member_id != null) {
                        console.log('member id not none: ' + member_id)
                        $('#shift_assigned_member_id').val(member_id.toString());
                    }

                    $('#shiftSubmit').prop('disabled', false);

                }else if(data.status == "error"){
                    alert(JSON.stringify(data));
                }
            }
        });

    }

    function updateTime(event, delta, revertFunc) {

        url = "/organization/" + orgid.toString() + "/shift/" + (event.id).toString() + "/time";


        var times = {start: event.start.toISOString(), end: event.end.toISOString()};

        $.ajax({
            headers: {
                'Accept': "application/json; charset=utf-8",
            },
            type: "POST",
            dataType: 'json',
            data: times,
            url: url,

            success: function(data)
            {
                console.log(JSON.stringify(data));

                if(data.status == "success"){


                }else if(data.status == "error"){
                    alert(JSON.stringify(data));
                    revertFunc();
                }

            }
        });

    }


    /*
    *
    * Code to Create new Position
    *
    */
    $('#createPositionSubmit').on('click', function() {
        var newPosition = {
            title: $('#title').val()
        };

        url = "/organization/" + orgid.toString() + "/create_position"

        $.ajax({
            type: "POST",
            url: url,
            data: $("#CreatePositionForm").serialize(), // serializes the form's elements.

            success: function(data)
            {

                if(data.status == "success"){
                    APP.addposition(newPosition);
                    APP.get_positions();
                    $('#CreatePositionModal').modal('hide');
                }else if(data.status == "error"){
                    alert(JSON.stringify(data));
                }
            }
        });
    });

    //Code to add a member to a position
    $('#AddUserToPositionSubmit').on('click', function() {
        console.log("AddUsertopositionsubmit pressed")

        //get the title of the position from the dropdownmenu
        var select = document.getElementById("positiondropdown");
        var positionid = select.options[select.selectedIndex].value;
        //var positionid = APP.vue.positions[index].id;
        //console.log(positionid) 
        var uid = APP.vue.userid;
        
        url = "/assign/" + uid.toString() + "/" + positionid.toString()

        $.ajax({
            type: "POST",
            url: url,

            success: function()
            {
                console.log("success")
            }
        });

        APP.get_assigned_positions();
        //$('#memberDetailModal').modal('hide');
    });

    //Code to invite a member
    $('#inviteMemberSubmit').on('click', function() {

        $('#inviteMemberSubmit').prop('disabled', true);

        var newUser = {
            first_name: $('#first_name').val(),
            last_name: $('#last_name').val(),
            email: $('#email').val()
        };

        var url = "/organization/" + orgid.toString() + "/invite"

        $.ajax({
            headers: {
                'Accept': "application/json; charset=utf-8",
            },
            type: "POST",
            url: url,
            data: $("#inviteMemberForm").serialize(), // serializes the form's elements.

            success: function(data)
            {

                if(data.status == "success"){
                    APP.adduser(newUser);
                    $('#inviteMemberModal').modal('hide');
                }else if(data.status == "error"){
                    console.log(JSON.stringify(data));
                    if ('message' in data) {
                        var html = '<p>' + data.message.toString() + '<p>';
                        $('#errorBody').append(html);
                    }
                    if ('errors' in data) {
                        for (var key in data.errors) {
                            var value = data.errors[key];
                            var html = '<p>' + key.toString() + ': ' + value.toString() + '<p>';
                            $('#errorBody').append(html);
                        }

                    }


                    // $('#errorBody').html(JSON.stringify(data.errors));
                    $('#errorModal').modal('show');
                }
            }
        });

        $('#inviteMemberSubmit').prop('disabled', false);

    });



});