import time
import requests
import zipfile
import os
from flask import current_app
from project.server.app.constant.constants import WORKING_DIRECTORY, MAX_DOWNLOAD_RETRIES, PORT


def start_archiving(urls):
    file_name = file_name_generator(urls)
    output_path = WORKING_DIRECTORY + file_name
    output_zip_file_name = file_name

    no_files = False
    unreachable_urls = []
    with zipfile.ZipFile(output_path, 'w', compression=zipfile.ZIP_DEFLATED) as my_zip:
        for url in urls:
            try:
                file_name = download_file_with_retry(url)
                if file_name is not None:
                    my_zip.write(filename=file_name)
                    os.remove(file_name)
                else:
                    unreachable_urls.append(url)
            except Exception as e:
                current_app.logger.error("Error while downloading file with url : " + url + " : " + str(e))
                unreachable_urls.append(url)

        list_of_zipped_files = my_zip.namelist()
        if len(list_of_zipped_files) == 0:
            no_files = True

    message = None
    success = True
    file_url = None
    if no_files:
        message = "Could not download files from urls: " + ",".join(unreachable_urls)
        success = False
    else:
        if len(unreachable_urls) > 0:
            message = "Files could not be fetched from : " + ",".join(unreachable_urls)
        else:
            message = "All Files successfully archived"

        file_url = "http://localhost:" + str(PORT) + "/archive/get/" + output_zip_file_name

    # call the predefined webhook here if needed as archive generation job is now completed
    job_completion_webhook(success, file_url, message)
    return prepare_task_completion_response(success, message, file_url)


def download_file(url):
    local_filename = url.split('/')[-1]
    with requests.get(url, stream=True) as r:
        r.raise_for_status()
        if r.status_code == 200:
            with open(local_filename, 'wb') as f:
                for chunk in r.iter_content(chunk_size=1024):
                    f.write(chunk)
        else:
            return None
    return local_filename


def fetch_and_save(url, local_filename):
    try:
        with requests.get(url, stream=True) as r:
            r.raise_for_status()
            if r.status_code == 200:
                with open(local_filename, 'wb') as f:
                    for chunk in r.iter_content(chunk_size=1024):
                        f.write(chunk)
                    return True
            else:
                return False
    except Exception as e:
        current_app.logger.error("Error in fetching and saving url : " + url + " : " + str(e))
        return False


def download_file_with_retry(url):
    local_filename = url.split('/')[-1]
    CURRENT_RETRY = 0
    while True:
        if CURRENT_RETRY < MAX_DOWNLOAD_RETRIES and fetch_and_save(url, local_filename):
            return local_filename
        elif CURRENT_RETRY < MAX_DOWNLOAD_RETRIES:
            current_app.logger.info("Retrying with val = " + str(CURRENT_RETRY) + " and url = " + url)
            CURRENT_RETRY += 1
            time.sleep(2)
        else:
            break

    return None


def file_name_generator(urls):
    output_file_name = ""
    for url in urls:
        file_name = url.split('/')[-1]
        file_name_without_extension = file_name.split('.')[0]
        output_file_name += file_name_without_extension + "_"
    return output_file_name + ".zip"


def prepare_task_completion_response(success, message, file_url):
    if file_url:
        return {"success": success, "message": message, "file_url": file_url}
    else:
        return {"success": success, "message": message}


def prepare_task_status_response(status, task_result):
    if task_result:
        return {"status": status, "data": task_result}
    else:
        return {"status": status}


def prepare_task_acceptance_response(is_success, task_id, error):
    if is_success:
        return {"success": is_success, "archive_hash": task_id}
    else:
        return {"success": is_success, "message": error}


def job_completion_webhook(success, file_url, message):
    try:
        # call the webhook on job completion here.
        # enactment of calling a rest api here
        current_app.logger.info("Job complete, Webhook being called")
        params = {
            "success": success,
            "file_url": file_url,
            "message": message
        }
        r = requests.get('http://www.google.com')
        current_app.logger.info("text returned ", r.text)
    except Exception as e:
        current_app.logger.error("error occurred while calling webhook ", e)
