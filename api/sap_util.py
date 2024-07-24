import json
import anthropic
import zipfile
import os

extract_dir = "zip_file"

with open('config.json', encoding='utf-8') as config_file:
    config_info_all = json.load(config_file)

config_details = config_info_all['claude']
MODEL_NAME = config_details['MODEL_NAME_SONNET']
CLIENT = anthropic.Anthropic(api_key=config_details['ANTHROPIC_API_KEY'])

temperature = 0
max_tokens = 4096


def javascript_analyze_func(language, code, xml_code):
    prompt_supplement = ""
    if language == "Japanese":
        prompt_supplement = """
            The following are tasks for analyzing javascript code. {{LANGUAGE}}

                <JS_CODE>
                {{JS_CODE}}
                </JS_CODE>

                <XML_CODE>
                {{XML_CODE}}
                </XML_CODE>

            The above javascript may contain content from multiple files, each separated by a '*******************************filename***********************************'.
            If there are multiple files, please split the files and sort them according to their calling relationships. Based on the actual file calling relationships, the main entrance should be the first, followed by the subroutines, named 1234 according to their execution order.

            1. 提供されたJavascript コード全体を読み、そのコードの機能の概要と要約を、番号付きのサブラベルを使用して提供してください。解析内容はテーブル形式で出力してください。
            - 例1. プログラムの機能概要:
                | No. | 機能概要 |
                |-----|----------|
                | 1 | バリアントで指定された条件に基づき、転記済未決済テーブル、未転記テーブルからデータを読み込む |
                | 2 | 会計定数マスタに登録されている条件に合った消込仕訳を未転記伝票にバッチインプットする |
                | 3 | 勘定科目間消込、得意先間消込、仕入先間消込、事業領域間消込の4種類の消込処理に対応 |
                | 4 | 各消込処理では、対象データを抽出し、集計・チェック後、消込仕訳伝票を作成する |
                | 5 | 作成した消込仕訳伝票をバッチインプットにより登録する |

            Only a functional overview is needed.
            As long as the above format is output, no other text is required.
            All outputs must be in {{LANGUAGE}}.

            """
    else:
        prompt_supplement = """
                The following are tasks for analyzing javascript code. {{LANGUAGE}}

                    <JS_CODE>
                    {{JS_CODE}}
                    </JS_CODE>

                    <XML_CODE>
                    {{XML_CODE}}
                    </XML_CODE>

                The above javascript code may contain content from multiple files, each separated by a '*******************************filename***********************************'.
                If there are multiple files, please split the files and sort them according to their calling relationships. Based on the actual file calling relationships, the main entrance should be the first, followed by the subroutines, named 1234 according to their execution order.

                Read the entire javascript code provided and provide an overview of the code's features and summaries using numbered sub labels. Output in the table format.
                - Example 1. Program features:
                    | No. | Function summary |
                    |-----|----------|
                    | 1 | Read data from the unregistered, unsettled table and untranslated table based on the conditions specified in the variant. 
                    | 2 | Batch input an entry into an untranslated slip corresponding to the condition registered in the accounting constant master. 
                    | 3 | Dealing with four types of cancellations between cancellations, delinquency, insertion and termination. 
                    | 4 | In each interruption processing, the object data is extracted, and after the totalization and the check, an interruption slip slip is made. 
                    | 5 | A batch entry is registered by batch input. 

                Only a functional overview is needed.
                The final output form must be in the form of [| No. | ...] start.
                As long as the above format is output, no other text is required.
                All outputs must be in {{LANGUAGE}}.

                """
    # If there are multiple files, please split the files and sort them according to their calling relationships, naming them 1234 based on the given file order.
    prompt_supplement = prompt_supplement.replace("{{ABAP_CODE}}", code).replace("{{LANGUAGE}}", language).replace(
        "{{XML_CODE}}", xml_code)

    # print(prompt_supplement)
    return js_order(language, prompt_supplement)


def js_order(language, prompt_supplement):
    system_temp = "You are an excellent Javascript code analysis expert. Analyze Javascript code according to user requirements. Note: All generated content must be in {}, and all results must be output in {}.".format(
        language, language)
    message = CLIENT.messages.create(
        model=MODEL_NAME,
        max_tokens=max_tokens,
        temperature=temperature,
        system=system_temp,
        messages=[
            {
                "role": "user",
                "content": prompt_supplement
            },
        ],
    )
    # return message.content[0].text.strip()
    return {"rCode": 1, "result": message.content[0].text.strip(), "input_tokens": message.usage.input_tokens, "output_tokens": message.usage.output_tokens}

def abap_analyze_func(language, code, xml_code):
    prompt_supplement = ""
    if language == "Japanese":
        prompt_supplement = """
            The following are tasks for analyzing SAP ABAP code. {{LANGUAGE}}
        
                <ABAP_CODE>
                {{ABAP_CODE}}
                </ABAP_CODE>
                
                <XML_CODE>
                {{XML_CODE}}
                </XML_CODE>
            
            The above SAP ABAP code may contain content from multiple files, each separated by a '*******************************filename***********************************'.
            If there are multiple files, please split the files and sort them according to their calling relationships. Based on the actual file calling relationships, the main entrance should be the first, followed by the subroutines, named 1234 according to their execution order.
            
            1. 提供されたSAP ABAPコード全体を読み、そのコードの機能の概要と要約を、番号付きのサブラベルを使用して提供してください。解析内容はテーブル形式で出力してください。
            - 例1. プログラムの機能概要:
                | No. | 機能概要 |
                |-----|----------|
                | 1 | バリアントで指定された条件に基づき、転記済未決済テーブル、未転記テーブルからデータを読み込む |
                | 2 | 会計定数マスタに登録されている条件に合った消込仕訳を未転記伝票にバッチインプットする |
                | 3 | 勘定科目間消込、得意先間消込、仕入先間消込、事業領域間消込の4種類の消込処理に対応 |
                | 4 | 各消込処理では、対象データを抽出し、集計・チェック後、消込仕訳伝票を作成する |
                | 5 | 作成した消込仕訳伝票をバッチインプットにより登録する |
            
            Only a functional overview is needed.
            As long as the above format is output, no other text is required.
            All outputs must be in {{LANGUAGE}}.
            
            """
    else:
        prompt_supplement = """
                The following are tasks for analyzing SAP ABAP code. {{LANGUAGE}}

                    <ABAP_CODE>
                    {{ABAP_CODE}}
                    </ABAP_CODE>

                    <XML_CODE>
                    {{XML_CODE}}
                    </XML_CODE>

                The above SAP ABAP code may contain content from multiple files, each separated by a '*******************************filename***********************************'.
                If there are multiple files, please split the files and sort them according to their calling relationships. Based on the actual file calling relationships, the main entrance should be the first, followed by the subroutines, named 1234 according to their execution order.

                Read the entire SAP ABAP code provided and provide an overview of the code's features and summaries using numbered sub labels. Output in the table format.
                - Example 1. Program features:
                    | No. | Function summary |
                    |-----|----------|
                    | 1 | Read data from the unregistered, unsettled table and untranslated table based on the conditions specified in the variant. 
                    | 2 | Batch input an entry into an untranslated slip corresponding to the condition registered in the accounting constant master. 
                    | 3 | Dealing with four types of cancellations between cancellations, delinquency, insertion and termination. 
                    | 4 | In each interruption processing, the object data is extracted, and after the totalization and the check, an interruption slip slip is made. 
                    | 5 | A batch entry is registered by batch input. 

                Only a functional overview is needed.
                The final output form must be in the form of [| No. | ...] start.
                As long as the above format is output, no other text is required.
                All outputs must be in {{LANGUAGE}}.

                """
    #If there are multiple files, please split the files and sort them according to their calling relationships, naming them 1234 based on the given file order.
    prompt_supplement = prompt_supplement.replace("{{ABAP_CODE}}", code).replace("{{LANGUAGE}}", language).replace("{{XML_CODE}}", xml_code)

    # print(prompt_supplement)
    return abap_order(language, prompt_supplement)

def abap_order(language, prompt_supplement):
    system_temp = "You are an excellent ABAP code analysis expert. Analyze ABAP code according to user requirements. Note: All generated content must be in {}, and all results must be output in {}.".format(
        language, language)
    message = CLIENT.messages.create(
        model=MODEL_NAME,
        max_tokens=max_tokens,
        temperature=temperature,
        system=system_temp,
        messages=[
            {
                "role": "user",
                "content": prompt_supplement
            },
        ],
    )
    # return message.content[0].text.strip()
    # return message
    return {"rCode": 1, "result": message.content[0].text.strip(), "input_tokens": message.usage.input_tokens, "output_tokens": message.usage.output_tokens}

def unzip_zipfile(file_path):
    xml_txt = ""
    abap_txt = ""
    js_txt = ""
    txt_type = ""
    if not os.path.exists(extract_dir):
        os.makedirs(extract_dir)

    with zipfile.ZipFile(file_path, 'r') as zip_ref:
        zip_ref.extractall(extract_dir)
        file_list = zip_ref.namelist()
        for file in file_list:
            with zip_ref.open(file) as myfile:
                if file.endswith(".xml"):
                    xml_txt += "\n*******************************" + os.path.basename(
                        file) + "***********************************\n\n" + myfile.read().decode('utf-8') + "\n"

                if file.endswith(".abap"):
                    abap_txt += "\n*******************************" + os.path.basename(
                        file) + "***********************************\n\n" + myfile.read().decode('utf-8') + "\n"
                    txt_type = "abap"

                if file.endswith(".js"):
                    js_txt += "\n*******************************" + os.path.basename(
                        file) + "***********************************\n\n" + myfile.read().decode('utf-8') + "\n"
                    txt_type = "js"

                if not os.path.isdir(os.getcwd() +"/"+extract_dir +"/" +file):
                    os.remove(os.getcwd() + "/" + extract_dir + "/" + file)


    return xml_txt,abap_txt,js_txt,txt_type
