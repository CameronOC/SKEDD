$(document).ready(function() {
    /*
    *
    * Code that applies to both modals
    *
    */
    var nextId

    $('.modal').on('hidden.bs.modal', function(){
        console.log('it works');
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
        events: [
            {
                title: 'Product Owner',
                start: '2016-10-26T06:00:00',
                end: '2016-10-26T14:00:00',
                description: 'Set the Product Backlog for the application',
                assigned: 'Chris Kempis',
                id: 1,
            },
            {
                title: 'Scrum Master',
                start: '2016-10-26T10:00:00',
                end: '2016-10-26T16:00:00',
                description: 'Run Scrum Meetings, update burnup chart and Scrum Board.',
                assigned: 'Philip Guther',
                id: 2,
            }
        ],
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
    var nextId = 3;

    $('#newPosition').on('click', function() {
        $('#createPositionModal').modal('show');
    });

    $('#createCancel').on('click', function() {

        var tempId = parseInt($('#createShiftId').text());
        $('#calendar').fullCalendar( 'removeEvents', tempId);
        $('#createShiftModal').modal('hide');
    });

});