import win32file
import win32con

def is_directory(self, path):
    try:
        attrs = win32file.GetFileAttributes(path)
        return attrs & win32con.FILE_ATTRIBUTE_DIRECTORY == win32con.FILE_ATTRIBUTE_DIRECTORY

    except:
        return False
