# -*- encoding:ascii -*-
from mako import runtime, filters, cache
UNDEFINED = runtime.UNDEFINED
__M_dict_builtin = dict
__M_locals_builtin = locals
_magic_number = 6
_modified_time = 1319302027.984112
_template_filename='web/templates/ios.html'
_template_uri='ios.html'
_template_cache=cache.Cache(__name__, _modified_time)
_source_encoding='ascii'
_exports = []


def render_body(context,**pageargs):
    context.caller_stack._push_frame()
    try:
        __M_locals = __M_dict_builtin(pageargs=pageargs)
        __M_writer = context.writer()
        # SOURCE LINE 1
        __M_writer(u'<!DOCTYPE html>\r\n<html>\r\n<head>\r\n<title>Clutch</title>\r\n<script type="text/javascript" src="static/jquery.js"></script>\r\n<script type="text/javascript" src="static/jquery-ui.js"></script>\r\n<script type="text/javascript" src="static/jquery.eventsource.js"></script>\r\n<script type="text/javascript" src="static/d3.min.js"></script>\r\n<script type="text/javascript" src="static/swipe.js"></script>\r\n<style type="text/css">\r\n    body,html{\r\n        margin:0;\r\n        padding:0;\r\n        height:100%\r\n    }\r\n    ul{\r\n        margin: 0;\r\n        padding:0;\r\n        list-style-type:none;\r\n        height:100%;\r\n        border:1px solid green;\r\n    }\r\n    .ControlGroup{\r\n        display: block;\r\n        height:100%;\r\n        width:100%;\r\n        border: 1px solid yellow;\r\n        float:left;\r\n    }\r\n    #slider{\r\n        display: block;\r\n        width:100%;\r\n        height:100%;\r\n        margin:0;\r\n        padding:0;\r\n        user-select: none;\r\n        -webkit-user-select: none;\r\n        -khtml-user-select: none;\r\n        -moz-user-select: none;\r\n        -o-user-select: none;\r\n        border: 1px solid red;\r\n        overflow:hidden;\r\n    }\r\n</style>\r\n<script type="text/javascript">\r\n    $(document).ready(function(){\r\n        var activeNumBoxes = [];\r\n        var active = 0;\r\n        \r\n        function startstream(){$.eventsource({\r\n            label: "nums",\r\n            url: "/sse-stream/",\r\n            dataType: "json",\r\n            message: function(msg){\r\n                $(".NumBox").each(function(i){\r\n                    varname = $(this).data(\'var\');\r\n                    if( varname in msg ){\r\n                        $(this).children(".Data").html(msg[varname]);\r\n                    }\r\n                });\r\n            }\r\n        });}\r\n        \r\n        function setupNumBoxes(){\r\n            $(".NumBox").html("<div class=\'Data\'>data</div><div class=\'Label\'>label</div>");\r\n            $(".NumBox").each(function(i){\r\n                $(this).children(".Label").html($(this).data("var"))\r\n                    .css("font-size",$(this).children(".Label").height()*0.90);\r\n                $(this).children(".Data")\r\n                    .css( "font-size",$(this).children(".Data").height()*0.80);\r\n            });\r\n        }\r\n        \r\n        setupNumBoxes();\r\n        startstream();\r\n\r\n        window.mySwipe = new Swipe(document.getElementById(\'slider\'));\r\n\r\n    });\r\n    \r\n    console.log("up and running");\r\n    \r\n\r\n</script>\r\n</head>\r\n<body>\r\n    <div id="slider" class="swipe">\r\n        <ul>\r\n            <li id="Settings" class="ControlGroup">\r\n                <ul>\r\n                    <li id="Boat" class="Box" onclick = "void(0)">Boat settings</li>\r\n                </ul>\r\n            </li>\r\n            <li id="RaceData" class="ControlGroup">\r\n                <ul>\r\n                    <li class="NumBox Box" data-var="TWA" onclick = "void(0)">TWA</li>\r\n                    <li class="NumBox Box" data-var="TWS" onclick = "void(0)">TWS</li>\r\n                </ul>\r\n            </li>\r\n            <li id="RaceManagement" class="ControlGroup LastGroup">\r\n                <ul>\r\n                    <li id="CourseSetup" class="Box" onclick = "void(0)">Create Course</li>\r\n                    <li id="StartScreen" class="Box" onclick = "void(0)">Start</li>\r\n                </ul>\r\n            </li>\r\n        </ul>\r\n    </div>\r\n</body>\r\n</html>')
        return ''
    finally:
        context.caller_stack._pop_frame()


