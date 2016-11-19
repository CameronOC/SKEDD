$(document).ready(function() {
    
    //timeId is used for FIRST TIME users creating events
    //Events saved in the DB will use DB id
    var timeId = 1;

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
        events: "/updatepreferences/" + current_user_id.toString() + "/" ,
        select: function(start, end, allDay) {
            var newEvent = {
                start: start,
                end: end,
                id: timeId,
            };
            
            $('#calendar').fullCalendar( 'renderEvent', newEvent , 'stick');
            timeId = timeId + 1;
            var newEventString = JSON.stringify(newEvent);
            newEventString = 'payload=' + newEventString

            $.ajax({
                url: "/updatepreferences/",
                type: "POST",
                data: newEventString,
                dataType: 'json',
                success: function(data) {
                    alert("Totes worked: " + newEventString);
                }
            });
        },

        eventClick: function (calEvent, jsEvent, view) {           
            $('#calendar').fullCalendar('removeEvents', calEvent._id);
            var calEventOutput = {
                start: calEvent.start,
                end: calEvent.end,
                id: calEvent.id,
            }

            calEventString = 'payload=' + JSON.stringify(calEventOutput);
            console.log("calEventString:  " + calEventString);

            $.ajax({
                url: "/updatepreferences/delete",
                type: "POST",
                data: calEventString,
                dataType: 'json',
                success: function(data) {
                    alert("Totes worked: " + newEventString);
                }
            });

        }
    });

});