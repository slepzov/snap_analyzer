import os
import shutil
import stat
import time

from django.shortcuts import render, get_object_or_404
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from rest_framework.viewsets import ModelViewSet

from snap_analyzer_django.models import GeneralCluster, EnclosureModel
from snap_analyzer_django.serializers import ClusterSerializer


def upload(request):
    if request.method == 'POST' and request.FILES['myfile']:
        myfile = request.FILES['myfile']
        fs = FileSystemStorage()
        filename = fs.save(myfile.name, myfile)
        uploaded_file_url = fs.url(filename)
        general_information = pars(filename)
        return render(request, 'snap_analyzer_django/upload.html', {
            'uploaded_file_url': uploaded_file_url, 'general_information': general_information,
        })
    return render(request, 'snap_analyzer_django/upload.html')


class ClusterView(ModelViewSet):
    queryset = GeneralCluster.objects.all()
    serializer_class = ClusterSerializer


def parser(request):
    clusters = GeneralCluster.objects.all()
    return render(request, 'snap_analyzer_django/main_app.html', {'clusters': clusters})


def orders_app(request):
    clusters = GeneralCluster.objects.all()
    return render(request, 'snap_analyzer_django/main_app.html', {'clusters': clusters})


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
    SVCOUT = ""

    files = os.listdir(DIRECTORY_NAME + "\dumps")
    for file_name in files:
        if "internalstorage" in file_name:
            INTERNALSTORAGE = file_name
        if "saout" in file_name:
            SAOUT = file_name
        if "machinenodeinfo" in file_name:
            MACHINENODEINFO = file_name
        if "svcout." + DIRECTORY_NAME.split(".")[1] in file_name:
            SVCOUT = file_name

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

    with open(DIRECTORY_NAME + "\dumps\\" + SVCOUT, "r", encoding="utf-8") as f:
        log_svcout = f.read().split("svcinfo")

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

    def parse_expansion(id, log, log_svcout, SERIAL_NUMBER, timestamp):
        expansion_dict = {"serial_number_cluster": SERIAL_NUMBER, "date_timestamp": timestamp, "id": id,
                          "temperature": "", "total_PSUs": "2", "id_node_left": "Null", "id_node_right": "Null",
                          "name_node_left": "Null", "name_node_right": "Null", "status_node_id_1": "Null",
                          "service_IP_address_node_id_1": "Null", "node_id_1_WWNN": "Null"}
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
        break_flag = False
        if expansion_dict["type"] == "control":
            for svcinfo_box in log_svcout:
                if "lsnode -delim : " in svcinfo_box and \
                    ("enclosure_serial_number:" + SERIAL_NUMBER) in svcinfo_box:
                    for parametr in svcinfo_box.strip().split("\n"):
                        if "id:" in parametr and expansion_dict["id_node_left"] == "Null":
                            expansion_dict["id_node_left"] = parametr.split(":")[1]
                        if "id:" in parametr and expansion_dict["id_node_right"] == "Null":
                            expansion_dict["id_node_right"] = parametr.split(":")[1]

        if expansion_dict["type"] == "control":
            for svcinfo_box in log_svcout:
                if "lsnode -delim : " + expansion_dict["id_node_left"] in svcinfo_box:
                    for parametr in svcinfo_box.strip().split("\n"):
                        if "name:" in parametr and expansion_dict["name_node_left"] == "Null":
                            expansion_dict["name_node_left"] = parametr.split(":")[1]
                        if "status:" in parametr and expansion_dict["status_node_id_1"] == "Null":
                            expansion_dict["status_node_id_1"] = parametr.split(":")[1]
                        if "service_IP_address:" in parametr and expansion_dict["service_IP_address_node_id_1"] == "Null":
                            expansion_dict["service_IP_address_node_id_1"] = parametr.split(":")[1]
                        if "WWNN:" in parametr and expansion_dict["node_id_1_WWNN"] == "Null":
                            expansion_dict["node_id_1_WWNN"] = parametr.split(":")[1]
        return expansion_dict

    for key in dict_id_enclosure:
        polka = parse_expansion(key, log, log_svcout, SERIAL_NUMBER, timestamp)
        enclosure = EnclosureModel(
            serial_number_cluster=polka["serial_number_cluster"],
            date_timestamp=polka["date_timestamp"],
            id_enclosure=polka["id"],
            type=polka["type"],
            temperature=polka["temperature"],
            total_PSUs=polka["total_PSUs"],
            product_MTM_enclosure=polka["product_MTM"],
            serial_number_enclosure=polka["serial_number"],
            status_enclosure=polka["status"],
            online_PSUs=polka["online_PSUs"],
            drive_slots=polka["drive_slots"],
            fault_LED=polka["fault_LED"],
            identify_LED=polka["identify_LED"],
            total_canisters=polka["total_canisters"],
            online_canisters=polka["online_canisters"],
            id_node_left=polka["id_node_left"],
            name_node_left=polka["name_node_left"],
            status_node_id_1=polka["status_node_id_1"],
            service_IP_address_node_id_1=polka["service_IP_address_node_id_1"],
            node_id_1_WWNN=polka["node_id_1_WWNN"],
        )
        enclosure.save()
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


def detail(request, blog_id):
    blog = get_object_or_404(GeneralCluster, pk=blog_id)
    enclosures = EnclosureModel.objects.all().filter(serial_number_cluster=blog.serial_number_cluster).filter(
        date_timestamp=blog.date_timestamp)
    return render(request, 'snap_analyzer_django/detail.html', {'blog': blog, 'enclosures': enclosures})
