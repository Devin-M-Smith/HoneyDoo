import base64

def encryptPassword(psswd):
    psswdASCII = psswd.encode('ascii')
    psswdBYTES = base64.b64encode(psswdASCII)
    finalPass = psswdBYTES.decode('ascii')
    return finalPass