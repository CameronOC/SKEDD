
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
        editable: isAdmin,
        selectable: isAdmin,
        selectHelper: true,
        events: "/organization/" + orgid.toString() + "/shifts",
        eventRender: function(event, element) {
            element.find('.fc-title').after("<span class=\"assigned\">" + event.assigned_member + "</span>");
            var checkbox = $('#' + event.position_id);
            if (checkbox.prop("checked") == false) {
                return false;
            }

        },
        eventClick:  function(event, jsEvent, view) {
            create = false;



            if (isAdmin) {
                $('#shiftSubmit').prop('disabled', true);
                $('#shiftDelete').show();
                $('#createMultipleShifts').hide();
                showAdminShiftModal(event);

            } else {
                showMemberShiftModal(event);
            }


        },
        select: function(start, end, allDay) {

            var newEvent = {
                start: start,
                end: end,
                id: 0,
                position_id: 0,
                description: '',
            };
            create = true;

            $('#calendar').fullCalendar( 'renderEvent', newEvent , 'stick');
            $('#shiftSubmit').prop('disabled', true);
            $('#shiftDelete').hide();
            $('#createMultipleShifts').show();
            showAdminShiftModal(newEvent);

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


    $('#shiftModal').on('hidden.bs.modal', function(){
        $('#shift_assigned_member_id').empty();
        $('#shift_position_id').val('0');
        $("#shift_repeat_list option:selected").prop("selected", false);
        $('#shift_repeating').prop('checked', false);
        $('#shift_repeat_list').hide();
    });

    $('#errorModal').on('hidden.bs.modal', function(){
        $('#errorBody').html('');
    });

    $(document).on('show.bs.modal', '.modal', function () {
        var zIndex = 1040 + (10 * $('.modal:visible').length);
        $(this).css('z-index', zIndex);
        setTimeout(function() {
            $('.modal-backdrop').not('.modal-stack').css('z-index', zIndex - 1).addClass('modal-stack');
        }, 0);
    });

    $('#shiftMemberModal').on('hidden.bs.modal', function(){
        $('#shiftMemberModal span').html('');
    });

    $('#shiftModal, #CreatePositionModal, #inviteMemberModal').on('hidden.bs.modal', function(){
        $(this).find("input,textarea").val('').end();
    });


    function showAdminShiftModal(shift) {
        $('#shift_start_time').val(shift.start.toISOString());
        $('#shift_end_time').val(shift.end.toISOString());
        $('#shift_id').val(shift.id);
        $('#shift_position_id').val(shift.position_id)
        if (create == false) {
            updateUsersForPosition(shift.position_id, shift.assigned_member_id);
        }
        $('#shift_description').val(shift.description);
        $('#shiftModal').modal('show');
    }

    function showMemberShiftModal(shift) {
        $('#shiftMemberTitle').html(shift.title);
        $('#assignedTo').html(shift.assigned_member);
        $('#description').html(shift.description);
        $('#startTime').html(shift.start.format('hh:mm a'));
        $('#endTime').html(shift.end.format('hh:mm a'));
        $('#shiftMemberModal').modal('show');

    }


    function createSuccess() {
        $('#calendar').fullCalendar( 'removeEvents', 0);
        $('#calendar').fullCalendar( 'refetchEvents' );
        $('#shiftModal').modal('hide');
    }

    /*
    *
    * Code to update the rendered shift representation if an
    * update shift ajax call is succesfully made
    *
    */
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

    /*
    *
    * Creates or Updates a shift with an ajax call
    * depending on whether the shift had just been created
    * or was being edited
    *
    */
    $('#shiftSubmit').on('click', function() {
        $('#shiftSubmit').prop('disabled', true);


        if (create == true) {
            url = "/organization/" + orgid.toString() + "/shift/create";
        } else {
            url = '/organization/' + orgid.toString() + '/shift/' + ($('#shift_id').val()).toString() + '/update';
        }

        var shiftDict = {
            shift_position_id: $('#shift_position_id').val(),
            shift_assigned_member_id: $('#shift_assigned_member_id').val(),
            shift_description: $('#shift_description').val(),
            shift_repeat_list: $('#shift_repeat_list').val(),
            shift_start_time: $('#shift_start_time').val(),
            shift_end_time: $('#shift_end_time').val()
        };


        $.ajax({
            headers: {
                'Accept': "application/json",
            },
            type: "POST",
            url: url,
            data: shiftDict,

            success: function(data)
            {
                if(data.status == "success"){

                    if (create) {
                        createSuccess();
                    } else {
                        updateSuccess(data.shift);
                    }

                }else if(data.status == "error"){
                    showErrorModal(data);
                    $('#shiftSubmit').prop('disabled', false);
                }
            }
        });



    });

    /*
    *
    * If shift creation is cancelled, the temporary shift that is created
    * by dragging on the calender needs to be deleted
    *
    */
    $('#shiftCancel').on('click', function() {
        if (create) {
            $('#calendar').fullCalendar( 'removeEvents', 0);
        }
        $('#shiftSubmit').prop('disabled', true);
        $('#shiftModal').modal('hide');
    });

    /*
    *
    * Makes an ajax call to delete a shift
    *
    */
    $('#shiftDelete').on('click', function() {

        var tempId = $('#shift_id').val();

        $('#shiftSubmit').prop('disabled', true);
        $('#shiftDelete').prop('disabled', true);
        url = '/organization/' + orgid.toString() + '/shift/' + (tempId).toString() + '/delete';

        $.ajax({
            headers: {
                'Accept': "application/json",
            },
            type: "DELETE",
            url: url,

            success: function(data)
            {

                if(data.status == "success"){

                    $('#calendar').fullCalendar( 'removeEvents', tempId);
                    $('#shiftModal').modal('hide');

                }else if(data.status == "error"){
                    showErrorModal(data)
                    $('#shiftSubmit').prop('disabled', false);

                }

                $('#shiftDelete').prop('disabled', false);
            }
        });


    });

    /*
    *
    * Whenever the create multiple toggle is changed, the week selector
    * toggles and the is cleared
    *
    */
    $('#shift_repeating').change(function() {
        $('#shift_repeat_list').toggle();
        $("#shift_repeat_list option:selected").prop("selected", false);
    });


    $('#drawerBody').on('change', '.position-toggle', function() {
        $('#calendar').fullCalendar( 'rerenderEvents' );
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
                'Accept': "application/json",
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
                        $('#shift_assigned_member_id').val(member_id.toString());
                    }

                    $('#shiftSubmit').prop('disabled', false);

                }else if(data.status == "error"){
                    showErrorModal(data)
                }
            }
        });

    }

    /*
    *
    * Makes an ajax call to update the start and end times of a shift
    *
    */
    function updateTime(event, delta, revertFunc) {

        url = "/organization/" + orgid.toString() + "/shift/" + (event.id).toString() + "/time";


        var times = {start: event.start.toISOString(), end: event.end.toISOString()};

        $.ajax({
            headers: {
                'Accept': "application/json",
            },
            type: "POST",
            dataType: 'json',
            data: times,
            url: url,

            success: function(data)
            {

                if(data.status == "success"){


                }else if(data.status == "error"){
                    showErrorModal(data)
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

        $('#createPositionSubmit').prop('disabled', true);

        var newPosition = {
            title: $('#name').val(),
            description: $('#description').val()
        };

        url = "/organization/" + orgid.toString() + "/create_position"

        $.ajax({
            type: "POST",
            url: url,
            data: newPosition, // serializes the form's elements.

            success: function(data)
            {

                if(data.status == "success"){
                    APP.addposition(newPosition);
                    APP.get_positions();
                    $('#CreatePositionModal').modal('hide');
                }else if(data.status == "error"){
                    showErrorModal(data);
                }
                $('#createPositionSubmit').prop('disabled', false);
            }
        });
    });

    /*
    *
    * Code to add a user to a position
    *
    */
    $('#AddUserToPositionSubmit').on('click', function() {
        //get the title of the position from the dropdownmenu
        var select = document.getElementById("positiondropdown");
        var positionid = select.options[select.selectedIndex].value;
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

    });

    /*
    *
    * Code to add a positon to a user
    *
    */
    $('#AddPositionToUserSubmit').on('click', function() {
        //get the title of the position from the dropdownmenu
        var select = document.getElementById("userdropdown");
        var uid = select.options[select.selectedIndex].value; 
        var pid = APP.vue.posid;
        
        url = "/assign/" + uid.toString() + "/" + pid.toString()

        $.ajax({
            type: "POST",
            url: url,

            success: function()
            {
                console.log("success")
            }
        });

        APP.get_assigned_users();

    });

    /*
    *
    * Code to a invite a member to a organization
    *
    */
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
                'Accept': "application/json",
            },
            type: "POST",
            url: url,
            data: newUser,

            success: function(data)
            {

                if(data.status == "success"){
                    APP.adduser(newUser);
                    $('#inviteMemberModal').modal('hide');
                }else if(data.status == "error"){
                    showErrorModal(data)
                }
            }
        });

        $('#inviteMemberSubmit').prop('disabled', false);

    });


    /*
    *
    * Displays a error modal
    *
    */
    function showErrorModal(data) {
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

        $('#errorModal').modal('show');

    }

    /*
    *
    * Code to delete a user from a organization
    *
    */
    $('#DeleteUserFromOrg').on('click', function() {
        var uid = APP.vue.userid;
        
        url = "/deleteuserfromorg/" + uid.toString() + "/" + orgid.toString()

        $.ajax({
            type: "POST",
            url: url,

            success: function()
            {
                console.log("success")
            }
        });

        APP.get_users();
    });

    /*
    *
    * Code to delete a position from a organization
    *
    */
    $('#DeletePositionFromOrg').on('click', function() {
        var posid = APP.vue.posid;
        
        url = "/deleteposition/" + posid.toString()

        $.ajax({
            type: "POST",
            url: url,

            success: function()
            {
                console.log("success")
            }
        });

        APP.get_positions();
        $('#calendar').fullCalendar( 'refetchEvents' );
    });

});