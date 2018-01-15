import os
import json
import datetime

golden_cases = ['test_firefox_facebook_ail_type_composerbox_1_txt', 'test_firefox_amazon_ail_type_in_search_field', 'test_firefox_facebook_ail_type_message_1_txt',
                'test_firefox_amazon_ail_hover_related_product_thumbnail', 'test_firefox_gsheet_ail_type_0', 'test_firefox_youtube_ail_type_in_search_field',
                'test_firefox_gmail_ail_reply_mail', 'test_firefox_gdoc_ail_type_0', 'test_firefox_gsearch_ail_select_search_suggestion', 'test_firefox_gmail_ail_open_mail',
                'test_firefox_facebook_ail_click_open_chat_tab', 'test_firefox_youtube_ail_select_search_suggestion', 'test_firefox_gsearch_ail_type_searchbox',
                'test_firefox_gslide_ail_pagedown_0', 'test_firefox_gsearch_ail_select_image_cat', 'test_firefox_outlook_ail_type_composemail_0',
                'test_firefox_facebook_ail_type_comment_1_txt', 'test_firefox_facebook_ail_click_open_chat_tab_emoji', 'test_firefox_outlook_ail_composemail_0',
                'test_firefox_gdoc_ail_pagedown_10_text', 'test_firefox_gmail_ail_compose_new_mail_via_keyboard', 'test_firefox_facebook_ail_scroll_home_1_txt',
                'test_firefox_amazon_ail_select_search_suggestion', 'test_firefox_gsheet_ail_clicktab_0', 'test_firefox_gslide_ail_type_0',
                'test_firefox_facebook_ail_click_close_chat_tab', 'test_firefox_facebook_ail_click_photo_viewer_right_arrow', 'test_firefox_gmail_ail_type_in_reply_field',
				'test_firefox_ymail_ail_compose_new_mail', 'test_firefox_ymail_ail_type_in_reply_field']

# get result folder and all folders under result folder
result_dir = os.path.abspath("..\\..\\result\\")
folders = os.listdir(result_dir)
 
# get all current folder list
date_result_dict = { x[4:8]:os.path.join(result_dir, x, "result.json") for x in folders }

# get maximum of 7 days
date_list = [ x[4:8] for x in folders if x.startswith("20")] 
date_list.sort(reverse=True)
date_list = date_list[:7]

cases = {}
# read all the json files and compare with golden sample
for date in date_list:
    file = date_result_dict[date]
    if os.path.exists(file):
        print "Now handling " + file + "(" + date + ")"
        with open(file, 'r') as fp:
            json_data = json.load(fp)
        if json_data["video-recording-fps"]:
            del json_data["video-recording-fps"]

        # get all missing cases
        missing_cases = list(set(golden_cases) - set(json_data.keys()))

        # get cases details
        detail = {}
        for test in json_data.keys():
            detail[test] = json_data[test]["detail"]

        # get cases time
        time = {}
        for test in json_data.keys():
            time[test] = round(json_data[test]["med_time"], 2)
			
        cases[date] = {"cases": len(json_data), "missing": missing_cases, "detail": detail, "time": time}

# output date with results # and missing golden sample to a file
# "(date)": { "cases": (number), "missing": (test lists), "change": (number&percentage) }
with open('webpage.json', 'w') as fp:
    json.dump(cases, fp)