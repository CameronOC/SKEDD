$(document).ready(function() {
    /*
    *
    * Code that applies to both modals
    *
    */
    var nextId

    $('.modal').on('hidden.bs.modal', function(){
        $(this).find("input,textarea").val('').end();
    });

    /*
    *
    * Code to Create new Events
    *
    */
    var nextId = 3;

    $('#createSubmit').on('click', function() {

        var tempId = parseInt($('#createShiftId').text());

        var eventlist = $("#calendar").fullCalendar('clientEvents', tempId);

        evento = eventlist[0];

        evento.title = $('#createShiftPosition').val();
        evento.description = $('#createShiftDescription').val();
        evento.assigned = $('#createShiftAssigned').val();

        $('#calendar').fullCalendar('updateEvent', evento);
        $('#createShiftModal').modal('hide');
        nextId = nextId + 1;
    });

    $('#createCancel').on('click', function() {

        var tempId = parseInt($('#createShiftId').text());
        $('#calendar').fullCalendar( 'removeEvents', tempId);
        $('#createShiftModal').modal('hide');
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
        nextId = nextId + 1;7
    });

    $('#editDelete').on('click', function() {

        var tempId = parseInt($('#editShiftId').text());
        $('#calendar').fullCalendar( 'removeEvents', tempId);
        $('#editShiftModal').modal('hide');
    });

    var getShifts = function() {

        url = "/organization/" + orgid.toString() + "/shifts"



        $.ajax({
            headers: {
                'Accept': "application/json; charset=utf-8",
            },
            type: "GET",
            url: url,
            success: function(data) {
                return data;
            }
        });

    }

    /*
    *
    * Initialize Calendar
    *
    */

    $('#calendar').fullCalendar({
        header: {
            left: 'prev,next today',
            center: 'title',
            right: 'month,agendaWeek,agendaDay'
        },
        defaultView: 'agendaWeek',
        allDaySlot: false,
        editable: true,
        selectable: true,
        selectHelper: true,
        events: getShifts(),
        eventRender: function(event, element) {
            element.find('.fc-title').after("<span class=\"assigned\">" + event.assigned + "</span>");
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
                id: nextId,
            };
            $('#calendar').fullCalendar( 'renderEvent', newEvent , 'stick');
            $('#createShiftStart').html(start.toString());
            $('#createShiftEnd').html(end.toString());
            $('#createShiftId').html(nextId.toString());
            $('#createShiftModal').modal('show');

        }
    });


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
        var positiontitle = select.options[select.selectedIndex].value;
        
        //get the userid
        var uid = APP.vue.userid;
        
        url = "/assign/" + uid.toString() + "/" + positiontitle.toString()

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