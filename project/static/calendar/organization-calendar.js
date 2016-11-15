$(document).ready(function() {
    /*
    *
    * Code that applies to both modals
    *
    */

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
    * Code to Create new Shifts
    *
    */

    $('#createSubmit').on('click', function() {
        $('#createSubmit').prop('disabled', true);

        url = url = "/organization/" + orgid.toString() + "/shift/create";

        $.ajax({
            headers: {
                'Accept': "application/json; charset=utf-8",
            },
            type: "POST",
            url: url,
            data: $("#createShiftForm").serialize(), // serializes the form's elements.

            success: function(data)
            {

                if(data.status == "success"){

                    console.log(JSON.stringify(data));

                    $('#calendar').fullCalendar( 'removeEvents', 0);

                    $('#calendar').fullCalendar( 'refetchEvents' )
                    $('#createShiftModal').modal('hide');

                }else if(data.status == "error"){
                    alert(JSON.stringify(data));
                }
            }
        });



    });

    $('#createCancel').on('click', function() {
        var tempId = parseInt($('#shift_id').val());
        $('#calendar').fullCalendar( 'removeEvents', tempId);
        $('#createSubmit').prop('disabled', true);
        $('#createShiftModal').modal('hide');
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
        $('#createSubmit').prop('disabled', false);

        url = "/organization/" + orgid.toString() + "/position/" + ($(this).val()).toString() + "/users";

        // alert(url);


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

                    var html = '<option class="generated" value="0"></option>';
                    $('#shift_assigned_member_id').append(html);

                    for (var i = 0; i < data.members.length; i++) {
                        var current = data.members[i];
                        var html = '<option class="generated" value="' + (current.id).toString() + '">' +
                                    current.first_name + ' ' + current.last_name + '</option>'
                        $('#shift_assigned_member_id').append(html);
                    }

                }else if(data.status == "error"){
                    alert(JSON.stringify(data));
                }
            }
        });


    });

    /*
    *
    * Code to Edit Events
    *
    */

     $('#editSubmit').on('click', function() {

        var tempId = parseInt($('#editShiftId').text());

        var eventlist = $("#calendar").fullCalendar('clientEvents', tempId);

        evento = eventlist[0];

        evento.title = $('#editShiftPosition').val();
        evento.description = $('#editShiftDescription').val();
        evento.assigned = $('#editShiftAssigned').val();

        $('#calendar').fullCalendar('updateEvent', evento);
        $('#editShiftModal').modal('hide');
    });

    $('#editDelete').on('click', function() {

        var tempId = parseInt($('#editShiftId').text());
        $('#calendar').fullCalendar( 'removeEvents', tempId);
        $('#editShiftModal').modal('hide');
    });

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
            $('#editShiftTitle').html(event.title);
            $('#editShiftPosition').val(event.title);
            $('#editShiftDescription').val(event.description);
            $('#editShiftAssigned').val(event.assigned);
            $('#editShiftStart').html(event.start.toString());
            $('#editShiftEnd').html(event.end.toString());
            $('#editShiftId').html(event.id);

            $('#editShiftModal').modal('show');
        },
        select: function(start, end, allDay) {

            var newEvent = {
                start: start,
                end: end,
                id: 0,
            };
            $('#calendar').fullCalendar( 'renderEvent', newEvent , 'stick');
            $('#shift_start_time').val(start.toISOString());
            $('#shift_end_time').val(end.toISOString());
            $('#shift_id').val('0');
            $('#createSubmit').prop('disabled', true);
            $('#createShiftModal').modal('show');

        }
    });


    if(calendar) {
      $(window).resize(function() {
        var calHeight = $(window).height()*0.67;
        $('#calendar').fullCalendar('option', 'height', calHeight);
      });
    };


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

        url = "/organization/" + orgid.toString() + "/invite"

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
                    alert(JSON.stringify(data));
                }
            }
        });

        $('#inviteMemberSubmit').prop('disabled', false);

    });



});