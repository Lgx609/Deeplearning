import os
import xml.etree.ElementTree as ET


def convert(size, box):
    x_center = (box[0] + box[1]) / 2.0
    y_center = (box[2] + box[3]) / 2.0
    x = x_center / size[0]
    y = y_center / size[1]
    w = (box[1] - box[0]) / size[0]
    h = (box[3] - box[2]) / size[1]
    return (x, y, w, h)


def convert_annotation(xml_files_path, save_txt_files_path):
    # 自动创建输出目录
    if not os.path.exists(save_txt_files_path):
        os.makedirs(save_txt_files_path)

    xml_files = os.listdir(xml_files_path)
    print("找到的XML文件:", xml_files)

    # 用于自动记录所有出现的类别及其ID（按首次出现顺序分配）
    class_map = {}
    current_id = 0

    for xml_name in xml_files:
        # 跳过非XML文件
        if not xml_name.endswith(".xml"):
            print(f"跳过非XML文件: {xml_name}")
            continue

        print(f"处理文件: {xml_name}")
        xml_file = os.path.join(xml_files_path, xml_name)
        out_txt_path = os.path.join(save_txt_files_path, xml_name.split(".")[0] + ".txt")

        try:
            tree = ET.parse(xml_file)
            root = tree.getroot()
            size = root.find("size")
            w = int(size.find("width").text)
            h = int(size.find("height").text)

            with open(out_txt_path, "w") as out_txt_f:
                for obj in root.iter("object"):
                    # 不过滤difficult，全部保留
                    cls = obj.find("name").text

                    # 自动为新类别分配ID
                    if cls not in class_map:
                        class_map[cls] = current_id
                        current_id += 1
                    cls_id = class_map[cls]

                    xmlbox = obj.find("bndbox")
                    b = (
                        float(xmlbox.find("xmin").text),
                        float(xmlbox.find("xmax").text),
                        float(xmlbox.find("ymin").text),
                        float(xmlbox.find("ymax").text),
                    )
                    bb = convert((w, h), b)
                    out_txt_f.write(f"{cls_id} {' '.join(map(str, bb))}\n")

        except Exception as e:
            print(f"处理{xml_name}时出错: {e}")

    # 输出类别映射关系（方便后续配置YOLO的names文件）
    print("\n类别ID映射关系:")
    for cls, idx in class_map.items():
        print(f"{idx}: {cls}")


if __name__ == "__main__":
    # VOC格式的xml标签文件路径
    xml_files1 = r"E:\data\annotations"
    # 转化为yolo格式的txt标签文件存储路径
    save_txt_files1 = r"E:\data\labels"

    convert_annotation(xml_files1, save_txt_files1)
    print("\n转换完成！请根据上述类别ID映射关系配置YOLO的names文件")
