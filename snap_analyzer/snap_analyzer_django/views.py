import os
import shutil
import stat
import tarfile

from django.shortcuts import render, get_object_or_404
from django.core.files.storage import FileSystemStorage
from django.utils.datastructures import MultiValueDictKeyError
from rest_framework.viewsets import ModelViewSet

from snap_analyzer_django.models import GeneralCluster, EnclosureModel, DriveModel, NodeModel
from snap_analyzer_django.serializers import ClusterSerializer


def upload(request):
    try:
        if request.method == 'POST' and request.FILES['myfile']:
            myfile = request.FILES['myfile']
            fs = FileSystemStorage()
            filename = fs.save(myfile.name, myfile)
            general_information = pars(filename)
            return render(request, 'snap_analyzer_django/upload.html', {'general_information': general_information})
        return render(request, 'snap_analyzer_django/upload.html')
    except tarfile.ReadError:
        os.remove(myfile.name)
        return render(request, 'snap_analyzer_django/upload.html')
    except MultiValueDictKeyError:
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
    SNAP_NAME = name
    SERIAL_NUMBER = ""
    DIRECTORY_NAME = SNAP_NAME[:-4]
    CODE_LEVEL = ""

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

    timestamp = date_timestamp + ' ' + time_timestamp

    cluster = GeneralCluster.objects.values().filter(serial_number_cluster=SERIAL_NUMBER).filter(
        date_timestamp=timestamp)

    if len(cluster) > 0:
        os.remove(SNAP_NAME)
        shutil.rmtree(DIRECTORY_NAME, onerror=removeReadOnly)
        return

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
                dict_id_enclosure[line.split(":")[0]] = line.split(":")[7]
            break

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
        expansion_dict = {"serial_number_cluster": SERIAL_NUMBER,
                          "date_timestamp": timestamp,
                          "id": id,
                          "temperature": "",
                          "total_PSUs": "2",
                          "online_batteries": 0,

                          "id_node_left": "Null",
                          "name_node_left": "Null",
                          "status_node_left": "Null",
                          "service_IP_address_node_left": "Null",
                          "IO_group_id_node_left": "Null",
                          "WWNN_node_left": "Null",
                          "IO_group_name_node_left": "Null",
                          "partner_node_id_node_left": "Null",
                          "partner_node_name_node_left": "Null",
                          "config_node_left": "Null",
                          "iscsi_name_node_left": "Null",
                          "service_gateway_node_left": "Null",
                          "service_subnet_mask_node_left": "Null",
                          "product_mtm_node_left": "Null",
                          "code_level_node_left": "Null",

                          "id_node_right": "Null",
                          "name_node_right": "Null",
                          "status_node_right": "Null",
                          "service_IP_address_node_right": "Null",
                          "IO_group_id_node_right": "Null",
                          "WWNN_node_right": "Null",
                          "IO_group_name_node_right": "Null",
                          "partner_node_id_node_right": "Null",
                          "partner_node_name_node_right": "Null",
                          "config_node_right": "Null",
                          "iscsi_name_node_right": "Null",
                          "service_gateway_node_right": "Null",
                          "service_subnet_mask_node_right": "Null",
                          "product_mtm_node_right": "Null",
                          "code_level_node_right": "Null",

                          }

        for svcinfo_box in log:
            if ("lsenclosure -delim : " + id) in svcinfo_box:
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
            if "lsenclosurebattery -delim :" in svcinfo_box:
                for parametr in svcinfo_box.strip().split("\n"):
                    if parametr.split(":")[0] == id and parametr.split(":")[2] == "online":
                        expansion_dict["online_batteries"] += 1
                break

        if expansion_dict["type"] == "control":
            for svcinfo_box in log_svcout:
                if "lsnode -delim : " in svcinfo_box and \
                        ("enclosure_serial_number:" + expansion_dict["serial_number"]) in svcinfo_box:
                    for parametr in svcinfo_box.strip().split("\n"):
                        if "id:" in parametr and expansion_dict["id_node_left"] == "Null":
                            expansion_dict["id_node_left"] = parametr.split(":")[1]
                            break
                if "lsnode -delim : " in svcinfo_box and \
                        ("enclosure_serial_number:" + expansion_dict["serial_number"]) in svcinfo_box and \
                        ("partner_node_id:" + expansion_dict["id_node_left"]) in svcinfo_box:
                    for parametr in svcinfo_box.strip().split("\n"):
                        if "id:" in parametr and expansion_dict["id_node_right"] == "Null":
                            expansion_dict["id_node_right"] = parametr.split(":")[1]
                            break

        if expansion_dict["type"] == "control":
            for svcinfo_box in log_svcout:
                if "lsnode -delim : " + expansion_dict["id_node_left"] in svcinfo_box:
                    print("lsnode -delim : " + expansion_dict["id_node_left"])
                    for parametr in svcinfo_box.strip().split("\n"):
                        if "name:" in parametr and expansion_dict["name_node_left"] == "Null":
                            expansion_dict["name_node_left"] = parametr.split(":")[1]
                        if "status:" in parametr and expansion_dict["status_node_left"] == "Null":
                            expansion_dict["status_node_left"] = parametr.split(":")[1]
                        if "service_IP_address:" in parametr and expansion_dict[
                                "service_IP_address_node_left"] == "Null":
                            expansion_dict["service_IP_address_node_left"] = parametr.split(":")[1]
                        if "IO_group_id:" in parametr and expansion_dict["IO_group_id_node_left"] == "Null":
                            expansion_dict["IO_group_id_node_left"] = parametr.split(":")[1]
                        if "WWNN:" in parametr and expansion_dict["WWNN_node_left"] == "Null":
                            expansion_dict["WWNN_node_left"] = parametr.split(":")[1]
                        if "IO_group_name:" in parametr and expansion_dict["IO_group_name_node_left"] == "Null":
                            expansion_dict["IO_group_name_node_left"] = parametr.split(":")[1]
                        if "partner_node_id:" in parametr and expansion_dict["partner_node_id_node_left"] == "Null":
                            expansion_dict["partner_node_id_node_left"] = parametr.split(":")[1]
                        if "partner_node_name:" in parametr and expansion_dict["partner_node_name_node_left"] == "Null":
                            expansion_dict["partner_node_name_node_left"] = parametr.split(":")[1]
                        if "config_node:" in parametr and expansion_dict["config_node_left"] == "Null":
                            expansion_dict["config_node_left"] = parametr.split(":")[1]
                        if "iscsi_name:" in parametr and expansion_dict["iscsi_name_node_left"] == "Null":
                            expansion_dict["iscsi_name_node_left"] = parametr.split(":")[1]
                        if "service_gateway:" in parametr and expansion_dict["service_gateway_node_left"] == "Null":
                            expansion_dict["service_gateway_node_left"] = parametr.split(":")[1]
                        if "service_subnet_mask:" in parametr and expansion_dict["service_subnet_mask_node_left"] == "Null":
                            expansion_dict["service_subnet_mask_node_left"] = parametr.split(":")[1]
                        if "product_mtm:" in parametr and expansion_dict["product_mtm_node_left"] == "Null":
                            expansion_dict["product_mtm_node_left"] = parametr.split(":")[1]
                        if "code_level:" in parametr and expansion_dict["code_level_node_left"] == "Null":
                            expansion_dict["code_level_node_left"] = parametr.split(":")[1]

                if "lsnode -delim : " + expansion_dict["id_node_right"] in svcinfo_box:
                    for parametr in svcinfo_box.strip().split("\n"):
                        if "name:" in parametr and expansion_dict["name_node_right"] == "Null":
                            expansion_dict["name_node_right"] = parametr.split(":")[1]
                        if "status:" in parametr and expansion_dict["status_node_right"] == "Null":
                            expansion_dict["status_node_right"] = parametr.split(":")[1]
                        if "service_IP_address:" in parametr and expansion_dict[
                                "service_IP_address_node_right"] == "Null":
                            expansion_dict["service_IP_address_node_right"] = parametr.split(":")[1]
                        if "IO_group_id:" in parametr and expansion_dict["IO_group_id_node_right"] == "Null":
                            expansion_dict["IO_group_id_node_right"] = parametr.split(":")[1]
                        if "WWNN:" in parametr and expansion_dict["WWNN_node_right"] == "Null":
                            expansion_dict["WWNN_node_right"] = parametr.split(":")[1]
                        if "IO_group_name:" in parametr and expansion_dict["IO_group_name_node_right"] == "Null":
                            expansion_dict["IO_group_name_node_right"] = parametr.split(":")[1]
                        if "partner_node_id:" in parametr and expansion_dict["partner_node_id_node_right"] == "Null":
                            expansion_dict["partner_node_id_node_right"] = parametr.split(":")[1]
                        if "partner_node_name:" in parametr and expansion_dict["partner_node_name_node_right"] == "Null":
                            expansion_dict["partner_node_name_node_right"] = parametr.split(":")[1]
                        if "config_node:" in parametr and expansion_dict["config_node_right"] == "Null":
                            expansion_dict["config_node_right"] = parametr.split(":")[1]
                        if "iscsi_name:" in parametr and expansion_dict["iscsi_name_node_right"] == "Null":
                            expansion_dict["iscsi_name_node_right"] = parametr.split(":")[1]
                        if "service_gateway:" in parametr and expansion_dict["service_gateway_node_right"] == "Null":
                            expansion_dict["service_gateway_node_right"] = parametr.split(":")[1]
                        if "service_subnet_mask:" in parametr and expansion_dict["service_subnet_mask_node_right"] == "Null":
                            expansion_dict["service_subnet_mask_node_right"] = parametr.split(":")[1]
                        if "product_mtm:" in parametr and expansion_dict["product_mtm_node_right"] == "Null":
                            expansion_dict["product_mtm_node_right"] = parametr.split(":")[1]
                        if "code_level:" in parametr and expansion_dict["code_level_node_right"] == "Null":
                            expansion_dict["code_level_node_right"] = parametr.split(":")[1]

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
            online_batteries=polka["online_batteries"],
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
            id_node_right=polka["id_node_right"],
        )
        enclosure.save()
        if polka["type"] == "control":
            node_left = NodeModel(
                serial_number_cluster=polka["serial_number_cluster"],
                date_timestamp=polka["date_timestamp"],
                serial_number_enclosure=polka["serial_number"],
                id_node=polka["id_node_left"],
                name_node=polka["name_node_left"],
                status_node=polka["status_node_left"],
                service_IP_address=polka["service_IP_address_node_left"],
                IO_group_id_node=polka["IO_group_id_node_left"],
                WWNN_node=polka["WWNN_node_left"],
                IO_group_name=polka["IO_group_name_node_left"],
                partner_node_id=polka["partner_node_id_node_left"],
                partner_node_name=polka["partner_node_name_node_left"],
                config_node=polka["config_node_left"],
                iscsi_name=polka["iscsi_name_node_left"],
                service_gateway=polka["service_gateway_node_left"],
                service_subnet_mask=polka["service_subnet_mask_node_left"],
                product_mtm=polka["product_mtm_node_left"],
                code_level=polka["code_level_node_left"],

            )
            node_left.save()
            node_right = NodeModel(
                serial_number_cluster=polka["serial_number_cluster"],
                date_timestamp=polka["date_timestamp"],
                serial_number_enclosure=polka["serial_number"],
                id_node=polka["id_node_right"],
                name_node=polka["name_node_right"],
                status_node=polka["status_node_right"],
                service_IP_address=polka["service_IP_address_node_right"],
                IO_group_id_node=polka["IO_group_id_node_right"],
                WWNN_node=polka["WWNN_node_right"],
                IO_group_name=polka["IO_group_name_node_right"],
                partner_node_id=polka["partner_node_id_node_right"],
                partner_node_name=polka["partner_node_name_node_right"],
                config_node=polka["config_node_right"],
                iscsi_name=polka["iscsi_name_node_right"],
                service_gateway=polka["service_gateway_node_right"],
                service_subnet_mask=polka["service_subnet_mask_node_right"],
                product_mtm=polka["product_mtm_node_right"],
                code_level=polka["code_level_node_right"],
            )
            node_right.save()
    all_drive = drive_parsing(log, dict_id_enclosure, timestamp)
    for drive in all_drive:
        disc = DriveModel(
            serial_number_cluster=SERIAL_NUMBER,
            serial_number_enclosure=drive["serial_number_enclosure"],
            date_timestamp=drive["timestamp"],
            drive_id=drive["drive_id"],
            drive_status=drive["drive_status"],
            drive_use=drive["drive_use"],
            capacity=drive["capacity"],
            drive_slot_id=drive["drive_slot_id"],
            id_enclosure=drive["id_enclosure"],
            vendor_id=drive["vendor_id"],
            product_id=drive["product_id"],
            transport_protocol=drive["transport_protocol"],
            FRU_part_number=drive["FRU_part_number"],
            FRU_identity=drive["FRU_identity"],
            mdisk_id=drive["mdisk_id"],
            mdisk_name=drive["mdisk_name"],
            firmware_level=drive["firmware_level"],
        )
        disc.save()

    os.remove(SNAP_NAME)
    shutil.rmtree(DIRECTORY_NAME, onerror=removeReadOnly)
    return general_information


def removeReadOnly(func, path, excinfo):
    os.chmod(path, stat.S_IWRITE)
    func(path)


def detail(request, blog_id):
    blog = get_object_or_404(GeneralCluster, pk=blog_id)
    clusters = GeneralCluster.objects.all().filter(serial_number_cluster=blog.serial_number_cluster)
    enclosures = EnclosureModel.objects.all().filter(serial_number_cluster=blog.serial_number_cluster).filter(
        date_timestamp=blog.date_timestamp)
    nodes = NodeModel.objects.all().filter(serial_number_cluster=blog.serial_number_cluster).filter(
        date_timestamp=blog.date_timestamp)
    drives = DriveModel.objects.all().filter(serial_number_cluster=blog.serial_number_cluster).filter(
        date_timestamp=blog.date_timestamp).order_by('drive_slot_id')
    return render(request, 'snap_analyzer_django/detail.html', {'blog': blog,
                                                                'enclosures': enclosures,
                                                                'clusters': clusters,
                                                                'nodes': nodes,
                                                                'drives': drives})


def drive_detail(request, blog_id_drive):
    blog_drive = get_object_or_404(DriveModel, pk=blog_id_drive)
    drives = DriveModel.objects.all().filter(serial_number_cluster=blog_drive.serial_number_cluster).filter(
        date_timestamp=blog_drive.date_timestamp).filter(id=blog_drive.id)
    enclosures = EnclosureModel.objects.all().filter(serial_number_enclosure=blog_drive.serial_number_enclosure).filter(
        date_timestamp=blog_drive.date_timestamp)
    return render(request, 'snap_analyzer_django/drive_detail.html', {'blog_drive': blog_drive,
                                                                      'drives': drives,
                                                                      'enclosures': enclosures})


def node_detail(request, blog_id_node):
    blog_node = get_object_or_404(NodeModel, pk=blog_id_node)
    return render(request, 'snap_analyzer_django/node_detail.html', {'blog_node': blog_node})


def drive_parsing(log, dict_id_enclosure, timestamp):
    all_drive_enclosure = []
    info_dict_drive = {}
    for svcinfo_box in log:
        if "lsdrive -delim :" in svcinfo_box:
            lsdrive = svcinfo_box.strip().split("\n")
            for id in range(2, len(lsdrive)):
                lsdrive_book = lsdrive[id].split(":")
                info_dict_drive["drive_id"] = lsdrive_book[0]
                info_dict_drive["drive_status"] = lsdrive_book[1]
                info_dict_drive["drive_use"] = lsdrive_book[3]
                info_dict_drive["capacity"] = lsdrive_book[5]
                info_dict_drive["drive_slot_id"] = int(lsdrive_book[10])
                info_dict_drive["id_enclosure"] = lsdrive_book[9]
                info_dict_drive["serial_number_enclosure"] = dict_id_enclosure[info_dict_drive["id_enclosure"]]
                info_dict_drive["timestamp"] = timestamp
                info_dict_drive["vendor_id"] = parse_property_drive(log, info_dict_drive["drive_id"], "vendor_id:")
                info_dict_drive["product_id"] = parse_property_drive(log, info_dict_drive["drive_id"], "product_id:")
                info_dict_drive["transport_protocol"] = parse_property_drive(log, info_dict_drive["drive_id"],
                                                                             "transport_protocol:")
                info_dict_drive["FRU_part_number"] = parse_property_drive(log, info_dict_drive["drive_id"],
                                                                          "FRU_part_number:")
                info_dict_drive["FRU_identity"] = parse_property_drive(log, info_dict_drive["drive_id"],
                                                                       "FRU_identity:")
                info_dict_drive["mdisk_id"] = parse_property_drive(log, info_dict_drive["drive_id"], "mdisk_id:")
                info_dict_drive["mdisk_name"] = parse_property_drive(log, info_dict_drive["drive_id"], "mdisk_name:")
                info_dict_drive["firmware_level"] = parse_property_drive(log, info_dict_drive["drive_id"],
                                                                         "firmware_level:")
                all_drive_enclosure.append(info_dict_drive)
                info_dict_drive = {}
            break

    return all_drive_enclosure


def parse_property_drive(log, drive_id, wanted_property):
    for svcinfo_box in log:
        if ("lsdrive -delim : " + drive_id) in svcinfo_box:
            for parametr in svcinfo_box.strip().split("\n"):
                if wanted_property in parametr:
                    return parametr.split(":")[1]
