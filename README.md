# generalUtils

    colorList  # list of tuples holding color info. each item = ([list of names for color], hex color string, rgb tuple)
    
    hex_to_rgb(hex)  # converts hex color string (starts with '#' or '0x') to (r, g, b)
    rgb_to_hex(rgb)  # converts (r, g, b) to hex string (without leading '#' or '0x')
    
    findColor(color)   
        Finds a color in colorList by name, rgb, or hex string.
        If a name string is passed, it must match exactly.
        If rgb (int, int, int) tuple is passed, if no exact match, returns closest color by tuple_distance between values.
        If hex string passed, if no exact match, converts to rgb and runs with that tuple.
    
    getCurrentColor(widget, color)
        Returns the 'color' portion of the widget's QPalette.
        Format of an element in colorList
            e.g. ([list of names for color], hex color string, rgb tuple)
        
        widget: QWidget, widget to inpect
        color: string or QPalette.ColorRole, portion of widget to inspect
            e.g. 'Window' or 'WindowText' or QtGui.QPalette.Background or QtGui.QPalette.Foreground
