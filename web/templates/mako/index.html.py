# -*- encoding:ascii -*-
from mako import runtime, filters, cache
UNDEFINED = runtime.UNDEFINED
__M_dict_builtin = dict
__M_locals_builtin = locals
_magic_number = 6
_modified_time = 1317381333.306739
_template_filename='web/templates/index.html'
_template_uri='index.html'
_template_cache=cache.Cache(__name__, _modified_time)
_source_encoding='ascii'
_exports = []


def render_body(context,**pageargs):
    context.caller_stack._push_frame()
    try:
        __M_locals = __M_dict_builtin(pageargs=pageargs)
        __M_writer = context.writer()
        # SOURCE LINE 1
        __M_writer(u'<html>\r\n<head>\r\n<title>Clutch</title>\r\n<link rel="stylesheet" type="text/css" href="static/css/clutch.css" />\r\n<script type="text/javascript" src="static/jquery.js"></script>\r\n<script type="text/javascript" src="static/jquery-ui.js"></script>\r\n<script type="text/javascript" src="static/jquery.eventsource.js"></script>\r\n<script type="text/javascript" src="static/d3.min.js"></script>\r\n<script type="text/javascript">\r\n    $(document).ready(function(){\r\n        activeNumBoxes = []\r\n        function startstream(){$.eventsource({\r\n            label: "nums",\r\n            url: "/sse-stream/",\r\n            dataType: "json",\r\n            message: function(msg){\r\n                activeNumBoxes.each(function(i){\r\n                    id = $(this).attr("id");\r\n                    if( id in msg ){\r\n                        $(this).children(".Data").html(msg[id]);\r\n                    }\r\n                });\r\n            }\r\n        });}\r\n        \r\n        function setupNumBoxes(){\r\n            activeNumBoxes = [];\r\n            boxes = $(".NumBox");\r\n            activeNumBoxes = boxes;\r\n            boxes.append("<div class=\'Data\'></div><div class=\'Label\'></div>");\r\n            boxes.each(function(i){\r\n                //_this = $(this)\r\n                //$(this).extend({ nb_label: $(this).children(".Label") });\r\n                //$(this).nb_label = $(this).children(".Label");\r\n                //$(this).nb_data  = $(this).children(".Data" );\r\n                //$(this).nb_label.html($(this).attr("id"));\r\n                $(this).children(".Label").html($(this).attr("id")).css("font-size",$(this).children(".Label").height()*0.90);\r\n                //$(this).nb_label.css("font-size",$(this).nb_label.height()*0.90);\r\n                //$(this).nb_data.css( "font-size",$(this).nb_data.height()*0.80);\r\n                $(this).children(".Data").css( "font-size",$(this).children(".Data").height()*0.80);\r\n                //$(this) = _this;\r\n            });            \r\n        }\r\n        setupNumBoxes();\r\n        activeNumBoxes = $(".NumBox");\r\n        startstream();\r\n\r\n\r\n    });\r\n\r\n</script>\r\n</head>\r\n<body>\r\n<div class="NumBox" id="TWA"></div>\r\n<div class="NumBox" id="TWS"></div><br>\r\n<div class="NumBox" id="Time"></div><br>\r\n</body>\r\n</html>')
        return ''
    finally:
        context.caller_stack._pop_frame()


