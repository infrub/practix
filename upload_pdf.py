from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
import sys


def main(pairname,weeki):
    print("upload pdf..")
    pdf_filename = "week_" + str(weeki).zfill(3) + ".pdf"
    pdf_pathname = "logs/" + pairname + "/" + pdf_filename


    gauth = GoogleAuth()
    gauth.CommandLineAuth()
    drive = GoogleDrive(gauth)

    folder_id = '19qGn9ufB0w4CcxQzqmPX5CZEVjs4mVlH'
    f = drive.CreateFile({'title': pdf_filename, 'mimeType': 'application/pdf', 'parents': [{'kind': 'drive#fileLink', 'id':folder_id}]})
    f.SetContentFile(pdf_pathname)
    f.Upload()

    print("done.")



if __name__ == "__main__":
    pairname = sys.argv[1]
    weeki = int(sys.argv[2])
    main(pairname,weeki)