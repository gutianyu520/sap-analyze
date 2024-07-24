from typing import Optional
from fastapi import APIRouter, File, UploadFile, Form
from typing import List
import os
import uuid
from service import utils
from service import abap_analysis
from api import sap_util

router = APIRouter()


@router.get("/hello")
def say_hello():
    return {"Hello": "World"}


# 多文件上传（表单格式）
@router.post("/abap_analyze")
async def upload_files(type: Optional[str] = Form(None),
                       programName: Optional[str] = Form(None),
                       programType: Optional[str] = Form(None),
                       functionGroup: Optional[str] = Form(None),
                       functionName: Optional[str] = Form(None),
                       className: Optional[str] = Form(None),
                       webydnpro: Optional[str] = Form(None),
                       webApp: Optional[str] = Form(None),
                       lang: Optional[str] = Form(None),
                       analysisType: Optional[str] = Form(None),
                       startScreen: Optional[str] = Form(None),
                       devMainFlow: UploadFile = File(None),
                       files: List[UploadFile] = File(None),
                       supFiles: List[UploadFile] = File(None), ):
    language = ""
    if lang == "E":
        language = "English"
    elif lang == "J":
        language = "Japanese"
    elif lang == "1":
        language = "Chinese"
    else:
        return {"rCode": 2, "result": "没有指定输出语言", "input_tokens": 0, "output_tokens": 0}

    # 升级检测
    if analysisType == "upgrade":
        if files is None or (not len(files) == 1):
            return {"rCode": 2, "result": "请上传zip文件", "input_tokens": 0, "output_tokens": 0}
        return tool_analyze(lang, files[0])

    # 概要说明
    if analysisType == "summary":
        analysisType = "概要解析"
    # UI解析
    elif analysisType == "ui":
        analysisType = "UI解析"
    # Flowchart
    elif analysisType == "flowchart":
        analysisType = "フローチャート生成"
    # 详细说明-开发主体流
    elif analysisType == "detailedMainFlow":
        analysisType = "メインフロー出力"
    # 详细说明-拼接结果
    elif analysisType == "detailedResult":
        analysisType = "サブルーチン実際実行流れ併合"
    else:
        return {"rCode": 2, "result": "分析类型指定有误", "input_tokens": 0, "output_tokens": 0}

    file_paths = []
    try:
        folder_id = str(uuid.uuid4())
        folder_path = os.path.join("unload_file/", folder_id)
        os.makedirs(folder_path, exist_ok=True)
        for file in files:
            file_path = os.path.join(folder_path, file.filename)
            print(file_path)
            file_paths.append(file_path)
            with open(file_path, "wb") as f:
                f.write(file.file.read())
    except Exception as e:
        print(e)

    # files
    abap_analysis.abap_xml_file_paths = file_paths

    #リザルトファイル入力
    if devMainFlow:
        abap_analysis.content_process_result = devMainFlow.file.read().decode("utf-8")

    #中継結果、補足情報入力
    basic_info = ""
    if supFiles:
        for file in supFiles:
            basic_info += file.file.read().decode("utf-8")

    if type == "FUGR" or type == "FUNC":
        type = "関数"

    try:
        history_show, result = abap_analysis.greet(history=[],
                                                   basic_info=basic_info,
                                                   input_sql_struct="",
                                                   input_program_main_name=programName if programName is not None else "",
                                                   input_function_name=functionName if functionName is not None else "",
                                                   input_function_group_name=functionGroup if functionGroup is not None else "",
                                                   input_dynpro_screen_start_num=startScreen if startScreen is not None else "",
                                                   type_options=type if type is not None else "",
                                                   programType_options=programType if programType is not None else "",
                                                   analysis_options=analysisType if analysisType is not None else "",
                                                   check_using_summary_result=False,
                                                   subroutine_start=1,
                                                   subroutine_end=999,
                                                   output_language=language, )
    except Exception as e:
        return {"rCode": 2, "result": str(e), "input_tokens": 0, "output_tokens": 0}

    result = ""
    input_tokens = 0
    output_tokens = 0
    for i in range(len(history_show)):
        if history_show[i] == ["", ""]:
            continue
        if "input_tokens" in history_show[i][1]:
            sp = history_show[i][1].split("\n")
            data = get_tokens(sp[len(sp) - 1])
            input_tokens += data["input_tokens"]
            output_tokens += data["output_tokens"]
        else:
            result += history_show[i][1]

    # 文件删除
    del_file(file_paths)

    result = {"rCode": 1, "result": result, "input_tokens": input_tokens, "output_tokens": output_tokens}
    return result


# @router.post("/tool_main_analyze")
# async def tool_analyze(lang: Optional[str] = Form(None),
#                        zipF: UploadFile = File(None)):
def tool_analyze(lang, zipF):
    language = ""
    if lang == "E":
        language = "English"
    elif lang == "J":
        language = "Japanese"
    elif lang == "1":
        language = "Chinese"
    else:
        return {"rCode": 2, "result": "没有指定输出语言", "input_tokens": 0, "output_tokens": 0}

    if not zipF:
        return {"rCode": 2, "result": "没有上传文件无法解析", "input_tokens": 0, "output_tokens": 0}

    if not zipF.filename.endswith("zip"):
        error_message = "请上传zip压缩文件"
        return {"rCode": 2, "result": error_message, "input_tokens": 0, "output_tokens": 0}

    try:
        folder_id = str(uuid.uuid4())
        folder_path = os.path.join("unload_file/", folder_id)
        os.makedirs(folder_path, exist_ok=True)
        file_path = os.path.join(folder_path, zipF.filename)
        with open(file_path, "wb") as f:
            f.write(zipF.file.read())

        xml_txt, abap_txt, js_txt, txt_type = sap_util.unzip_zipfile(file_path)
        if txt_type == "abap":
            # abap解析
            files_content_temp = sap_util.abap_analyze_func(language, abap_txt, "")
        elif txt_type == "js":
            # js解析
            files_content_temp = sap_util.javascript_analyze_func(language, js_txt, xml_txt)
        else:
            files_content_temp = sap_util.abap_analyze_func(language, "", xml_txt)
        os.remove(file_path)
    except UnicodeDecodeError as e:
        error_message = f"Unicode解码错误: {str(e)}"
        return {"rCode": 2, "result": error_message, "input_tokens": 0, "output_tokens": 0}

    return files_content_temp


def get_tokens(token_str):
    pairs = token_str.split(", ")
    data = {}
    for pair in pairs:
        key, value = pair.split("=")
        data[key.strip()] = int(value)
    return data


def del_file(file_paths):
    for file_path in file_paths:
        os.remove(file_path)
