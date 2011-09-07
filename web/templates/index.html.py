# -*- encoding:ascii -*-
from mako import runtime, filters, cache
UNDEFINED = runtime.UNDEFINED
__M_dict_builtin = dict
__M_locals_builtin = locals
_magic_number = 6
_modified_time = 1314858188.504399
_template_filename='templates/index.html'
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
        __M_writer(u'<html>\r\n<head>\r\n<title>Clutch</title>\r\n<script type="text/javascript" src="static/jquery.js"></script>\r\n<script type="text/javascript" src="static/jquery-ui.js"></script>\r\n<script type="text/javascript" src="static/jquery.eventsource.js"></script>\r\n<script type="text/javascript">\r\n    /*var stream = new EventSource(\'/sse-stream/\');\r\n    stream.addEventListener(\'message\', function(e){\r\n        var vars = jQuery.parseJSON( e.data );\r\n        $("span.TWASSE").html(vars[\'TWA\']);\r\n        },false);\r\n    */\r\n    $(document).ready(function(){\r\n        function startstream(){$.eventsource({\r\n            label: "nums",\r\n            url: "/sse-stream/",\r\n            dataType: "json",\r\n            open: function( data ){\r\n                console.log( "opened connection" );\r\n                console.log( data );\r\n            },\r\n            message: function(data){\r\n                console.log( data );\r\n                for( i in data ){\r\n                    $("span." + i).html(data[i]);\r\n                }\r\n            }\r\n        });}\r\n        \r\n        startstream();\r\n        \r\n        $("button").button();\r\n        $("button").html("Pause");\r\n        $("button").click(function(e){\r\n            if( $("button").html() == "Pause" ){\r\n                $("button").html("Start");\r\n                $.eventsource("close","nums");\r\n            }else{\r\n                $("button").html("Pause");\r\n                startstream();\r\n            }\r\n/*            if( e.currentTarget.html() == "Pause" ){\r\n                e.currentTarget.html("Start");\r\n                \r\n            }else{\r\n                e.currentTarget.html("Pause");\r\n                startstream;\r\n            }*/\r\n        });\r\n    });\r\n\r\n\t/*function updatePage(data){\r\n\t\tvar vars = jQuery.parseJSON( data );\r\n\t\t<!--$("body").append("<br>got update".concat(data))-->\r\n\t\tfor( i in vars){\r\n\t\t\t\t$("span.".concat(i)).html(vars[i]);\r\n\t\t}\r\n\t}*/\r\n</script>\r\n</head>\r\n<body>\r\n<h3>Clutch Data</h3>\r\n<span id="data" class="TWA">0.00</span>\r\n<span class="TWS"></span><br>\r\n<span class="Time"></span><br>\r\n<button></button>\r\n<!--<iframe id="StreamFrame" name="StreamFrame" style="width:0px; height:0px;border:0px" src="/stream/"></iframe>-->\r\n</body>\r\n</html>')
        return ''
    finally:
        context.caller_stack._pop_frame()


