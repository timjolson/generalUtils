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


### differential_solver.DESolver
Extension of class version of [scipy.optimize.differential_evolution](https://docs.scipy.org/doc/scipy/reference/generated/scipy.optimize.differential_evolution.html) that can be saved and reloaded.

Also see: scipy.optimize._differentialevolution.DifferentialEvolutionSolver

    from differential_evolver import DESolver
    import json
    
    # Make the object
    des = DESolver(func, bounds, ...)
    
    # Save the object's state to a file
    json.dump(des.state, open(file, 'w'))
    
    # Load an object from a file
    reloaded = DESolver.from_json(open(file, 'r'), func, args, callback)
    
    # Save the object's state in memory
    backup = des.state.copy()
    
    # Load an object from a state in memory
    des = DESolver.from_state(backup, func, args, callback)
    
    # Continue solving/iterating as usual
    x, y = next(des)
    # or
    des.solve()
