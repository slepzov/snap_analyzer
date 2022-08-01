import tarfile
import sys
import os

SNAP_NAME = sys.argv[1]
SERIAL_NUMBER = ""
DIRECTORY_NAME = SNAP_NAME[:-4]
CODE_LEVEL = ""

if __name__ == "__main__":
    with tarfile.open(SNAP_NAME) as tar:
        tar.extractall(path=DIRECTORY_NAME)

INTERNALSTORAGE = ""
SAOUT = ""
MACHINENODEINFO = ""

files = os.listdir(DIRECTORY_NAME + "\dumps")
for file_name in files:
    if "internalstorage" in file_name:
        INTERNALSTORAGE = file_name
    if "saout" in file_name:
        SAOUT = file_name
    if "machinenodeinfo" in file_name:
        MACHINENODEINFO = file_name

PRODUCT_NAME = ""
with open(DIRECTORY_NAME + "\dumps\\" + SAOUT) as f:
    for line in f:
        if "product_name" in line:
            PRODUCT_NAME = line[13:]
            break

TYPE = ""

with open(DIRECTORY_NAME + "\dumps\\" + INTERNALSTORAGE) as f:
    for line in f:
        if ":control:" in line:
            svcinfo_lsenclosure = line.split(":")
            if len(svcinfo_lsenclosure) == 9:
                TYPE = svcinfo_lsenclosure[3]
                SERIAL_NUMBER = svcinfo_lsenclosure[4]
                break
            else:
                TYPE = svcinfo_lsenclosure[6]
                SERIAL_NUMBER = svcinfo_lsenclosure[7]
                break

with open(DIRECTORY_NAME + "\dumps\\" + MACHINENODEINFO) as f:
    for line in f:
        if "config node" in line:
            CODE_LEVEL = line.split(",")[8].split(" ")[0]
            break

date_timestamp = SAOUT.split(".")[-2][4:] + "." + SAOUT.split(".")[-2][2:4] + "." + "20" + SAOUT.split(".")[-2][0:2]
time_timestamp = SAOUT.split(".")[-1][0:2] + ":" + SAOUT.split(".")[-1][2:4] + ":" + SAOUT.split(".")[-1][4:]

print(f"Главный файл = {INTERNALSTORAGE}")
print(f"saout файл = {SAOUT}")
print(f"Product_name: {PRODUCT_NAME}")
print(f"Type: {TYPE}")
print(f"Серийный номер СХД: {SERIAL_NUMBER}")
print(f"Code level: {CODE_LEVEL}")
print(f"Timestamp: {date_timestamp} {time_timestamp}")


with open(DIRECTORY_NAME + "\dumps\\" + INTERNALSTORAGE) as f:
    log = f.read().split("svcinfo")

number_enclosure = ""

for svcinfo_box in log:
    if "lsenclosure -delim" in svcinfo_box:
       # print(svcinfo_box.strip().split("\n"))
        number_enclosure = len(svcinfo_box.strip().split("\n")[2:])
        break

print(f"Количество полок: {number_enclosure}")