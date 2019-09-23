def __init_plugin__(app=None):
    from pymol.plugins import addmenuitemqt
    addmenuitemqt('Enlighten', run_plugin_gui)


def run_plugin_gui():
    import sys
    import os
    sys.path.append(os.path.dirname(__file__))
    from windows.windows import WindowManager
    from windows.main import MainWindow
    from controller import EnlightenController

    global main_window  # To keep garbage collector from deleting main_window

    window_manager = WindowManager()
    main_window = MainWindow(window_manager)
    window_manager.bind_all(EnlightenController())

    main_window.show()
