import os
import shutil
import stat

from django.shortcuts import render
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from rest_framework.viewsets import ModelViewSet

from snap_analyzer_django.models import GeneralCluster
from snap_analyzer_django.serializers import ClusterSerializer


def upload(request):
    if request.method == 'POST' and request.FILES['myfile']:
        myfile = request.FILES['myfile']
        fs = FileSystemStorage()
        filename = fs.save(myfile.name, myfile)
        uploaded_file_url = fs.url(filename)
        general_information = pars(filename)
        return render(request, 'snap_analyzer_django/main_app.html', {
            'uploaded_file_url': uploaded_file_url, 'general_information': general_information,
        })
    return render(request, 'snap_analyzer_django/upload.html')


class ClusterView(ModelViewSet):
    queryset = GeneralCluster.objects.all()
    serializer_class = ClusterSerializer


def parser(request):
    return render(request, 'snap_analyzer_django/main_app.html')


def orders_app(request):
    return render(request, 'snap_analyzer_django/main_app.html')


def pars(name):
    import tarfile
    import sys

    SNAP_NAME = name
    SERIAL_NUMBER = ""
    DIRECTORY_NAME = SNAP_NAME[:-4]
    CODE_LEVEL = ""
    ID_CONTROL = ""

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
                PRODUCT_NAME = line[13:].strip()
                break

    TYPE = ""

    with open(DIRECTORY_NAME + "\dumps\\" + INTERNALSTORAGE) as f:
        for line in f:
            if ":control:" in line:
                svcinfo_lsenclosure = line.split(":")
                if len(svcinfo_lsenclosure) == 9:
                    TYPE = svcinfo_lsenclosure[3]
                    SERIAL_NUMBER = svcinfo_lsenclosure[4]
                    ID_CONTROL = svcinfo_lsenclosure[0]
                    break
                else:
                    TYPE = svcinfo_lsenclosure[6]
                    SERIAL_NUMBER = svcinfo_lsenclosure[7]
                    ID_CONTROL = svcinfo_lsenclosure[0]
                    break

    with open(DIRECTORY_NAME + "\dumps\\" + MACHINENODEINFO) as f:
        for line in f:
            if "config node" in line:
                CODE_LEVEL = line.split(",")[8].split(" ")[0]
                break

    date_timestamp = SAOUT.split(".")[-2][4:] + "." + SAOUT.split(".")[-2][2:4] + "." + "20" + SAOUT.split(".")[-2][0:2]
    time_timestamp = SAOUT.split(".")[-1][0:2] + ":" + SAOUT.split(".")[-1][2:4] + ":" + SAOUT.split(".")[-1][4:]

    timestamp = date_timestamp + ' ' + time_timestamp

    # print(f"Главный файл = {INTERNALSTORAGE}")
    # print(f"saout файл = {SAOUT}")
    # print(f"Product_name: {PRODUCT_NAME}")
    # print(f"Type: {TYPE}")
    # print(f"Серийный номер СХД: {SERIAL_NUMBER}")
    # print(f"Code level: {CODE_LEVEL}")
    # print(f"Timestamp: {date_timestamp} {time_timestamp}")

    with open(DIRECTORY_NAME + "\dumps\\" + INTERNALSTORAGE) as f:
        log = f.read().split("svcinfo")

    number_enclosure = ""
    dict_id_enclosure = {}

    for svcinfo_box in log:
        if "lsenclosure -delim" in svcinfo_box:
            number_enclosure = len(svcinfo_box.strip().split("\n")[2:])
            for line in svcinfo_box.strip().split("\n")[2:]:
                dict_id_enclosure[line.split(":")[0]] = line.split(":")[2]
            break

    # print(dict_id_enclosure)
    # print(f"Количество полок: {number_enclosure}")

    general_information = {'product_name': PRODUCT_NAME, 'type': TYPE,
                           'serial_number': SERIAL_NUMBER, 'code_level': CODE_LEVEL,
                           'date_timestamp': timestamp, 'number_of_enclosure': number_enclosure}

    cluster = GeneralCluster(
        serial_number_cluster=SERIAL_NUMBER,
        date_timestamp=timestamp,
        product_name=PRODUCT_NAME,
        type=TYPE,
        code_level=CODE_LEVEL,
        number_of_enclosure=number_enclosure
    )
    cluster.save()

    def parse_expansion(id, log):
        expansion_dict = {"id": id, "temperature": "", "total_PSUs": "2"}
        for svcinfo_box in log:
            if ("lsenclosure -delim : " + id) in svcinfo_box:
                # print(svcinfo_box.strip().split("\n"))
                for parametr in svcinfo_box.strip().split("\n"):
                    if "product_MTM:" in parametr:
                        expansion_dict["product_MTM"] = parametr.split(":")[1]
                    if "serial_number:" in parametr:
                        expansion_dict["serial_number"] = parametr.split(":")[1]
                    if "ambient_temperature:" in parametr:
                        expansion_dict["temperature"] = parametr.split(":")[1]
                    if "status:" in parametr:
                        expansion_dict["status"] = parametr.split(":")[1]
                    if "type:" in parametr:
                        expansion_dict["type"] = parametr.split(":")[1]
                    if "total_PSUs:" in parametr:
                        expansion_dict["total_PSUs"] = parametr.split(":")[1]
                    if "online_PSUs:" in parametr:
                        expansion_dict["online_PSUs"] = parametr.split(":")[1]
                    if "drive_slots:" in parametr:
                        expansion_dict["drive_slots"] = parametr.split(":")[1]
                    if "fault_LED:" in parametr:
                        expansion_dict["fault_LED"] = parametr.split(":")[1]
                    if "identify_LED:" in parametr:
                        expansion_dict["identify_LED"] = parametr.split(":")[1]
                    if "total_canisters:" in parametr:
                        expansion_dict["total_canisters"] = parametr.split(":")[1]
                    if "online_canisters:" in parametr:
                        expansion_dict["online_canisters"] = parametr.split(":")[1]
                break
        return expansion_dict

    for key in dict_id_enclosure:
        polka = parse_expansion(key, log)
        # print("___________________________________________________________________________________")
        # print("id: " + polka["id"])
        # print("Enc_type: " + polka["product_MTM"] + "(" + polka["type"] + ")")
        # print("SN: " + polka["serial_number"])
        # print("Status: " + polka["status"])
        # print("Temperature: " + polka["temperature"])
        # print("Nodes: " + polka["total_canisters"] + "/" + polka["online_canisters"])
        # print("PSUs: " + polka["online_PSUs"] + "/" + polka["total_PSUs"])

    os.remove(SNAP_NAME)
    shutil.rmtree(DIRECTORY_NAME, onerror=removeReadOnly)
    return general_information


def removeReadOnly(func, path, excinfo):
    os.chmod(path, stat.S_IWRITE)
    func(path)
