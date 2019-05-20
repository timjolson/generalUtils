import os
#TODO: pytest this module


def get_designer_plugin_directory():
    from PyQt5.QtCore import QLibraryInfo
    info = QLibraryInfo.location(QLibraryInfo.PluginsPath)
    plugins_path = os.path.join(str(info), "designer", "python")
    return plugins_path


def install_plugin_files(files):
    plugins_path = get_designer_plugin_directory()

    if isinstance(files, str):
        files = [files]

    if not os.path.exists(plugins_path):
        os.makedirs(plugins_path)

    for plugin in files:
        path = os.path.abspath(plugin)
        directory, file_name = os.path.split(path)
        output_path = os.path.join(plugins_path, file_name)
        print("Copying", path, "to", plugins_path)
        open(output_path, "wb").write(open(path, "rb").read())


def compile_ui_file(files, output_files=None):
    import PyQt5.uic

    if isinstance(files, str) and (isinstance(output_files, str) or output_files is None):
        files = [files]
        output_files = [output_files or None]

    for path, output in zip(files, output_files):
        path = os.path.abspath(path)
        directory, file_name = os.path.split(path)
        file_name = "ui_" + file_name.replace(".ui", os.extsep + "py")
        output_path = os.path.join(path, file_name)

        print("Compiling", path, "to", output_path)
        input_file = open(path)
        output_file = output or open(output_path, "w")
        PyQt5.uic.compileUi(input_file, output_file)
        input_file.close()
        output_file.close()
