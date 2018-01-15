var webpage_data = "http://localhost:8000/scripts/status/webpage.json";
var cached_webpage_data = cachedFetch(webpage_data);

var golden_cases = ['test_firefox_facebook_ail_type_composerbox_1_txt', 'test_firefox_amazon_ail_type_in_search_field', 'test_firefox_facebook_ail_type_message_1_txt',
				'test_firefox_amazon_ail_hover_related_product_thumbnail', 'test_firefox_gsheet_ail_type_0', 'test_firefox_youtube_ail_type_in_search_field',
				'test_firefox_gmail_ail_reply_mail', 'test_firefox_gdoc_ail_type_0', 'test_firefox_gsearch_ail_select_search_suggestion', 'test_firefox_gmail_ail_open_mail',
				'test_firefox_facebook_ail_click_open_chat_tab', 'test_firefox_youtube_ail_select_search_suggestion', 'test_firefox_gsearch_ail_type_searchbox',
				'test_firefox_gslide_ail_pagedown_0', 'test_firefox_gsearch_ail_select_image_cat', 'test_firefox_outlook_ail_type_composemail_0',
				'test_firefox_facebook_ail_type_comment_1_txt', 'test_firefox_facebook_ail_click_open_chat_tab_emoji', 'test_firefox_outlook_ail_composemail_0',
				'test_firefox_gdoc_ail_pagedown_10_text', 'test_firefox_gmail_ail_compose_new_mail_via_keyboard', 'test_firefox_facebook_ail_scroll_home_1_txt',
				'test_firefox_amazon_ail_select_search_suggestion', 'test_firefox_gsheet_ail_clicktab_0', 'test_firefox_gslide_ail_type_0',
				'test_firefox_facebook_ail_click_close_chat_tab', 'test_firefox_facebook_ail_click_photo_viewer_right_arrow', 'test_firefox_gmail_ail_type_in_reply_field',
				'test_firefox_ymail_ail_compose_new_mail', 'test_firefox_ymail_ail_type_in_reply_field']

var switchDisplay = function(id) {
	let elem = document.getElementById(id);
	let display = elem.style.display;
	if(display == "none") {
		document.getElementById(id).style.display = "";
	} else {
		document.getElementById(id).style.display = "none";
	}
}

var getLast7Days = function() {
    let result = [];
    for (let i = 0; i < 7; i++) {
        let d = new Date();
        d.setDate(d.getDate() - i);
		
		let dd = d.getDate();
		let mm = d.getMonth() + 1; 
		
		if(dd < 10) dd = '0' + dd; 
		if(mm < 10) mm = '0' + mm; 
		
		let date = mm + dd;
		
        result.push(date);
    }

    return result;
}

var last7Days = getLast7Days();

cached_webpage_data.then(function(input) {
	var generateTableNumTable = function() {
		let content = "<table id='mainTable' class='paleBlueRows'><thead><tr><th></th>";

		for (let i = 0; i < 7; i++) {
			content += "<th style='text-align:center;'>" + last7Days[i] + "</th>";
		}
		content += "</tr></thead><tfoot>";

		content += "<tr class='hover'><td class='text-left hover'># of Test Cases Ran</td>";
		for (let i = 0; i < 7; i++) {
			if( last7Days[i] in input) {
				content += "<td class='text-left hover'>" + input[last7Days[i]]['cases'] + "</td>";
			} else {
				content += "<td class='text-left hover'></td>";
			}
		}
		content += "</tr></tfoot><tbody class=table-hover'>";
		
		for (let i = 0; i < golden_cases.length; i++) {
			content += "<tr><td style='font-weight:bold;'>" + golden_cases[i] + "</td>";
			for (let j = 0; j < 7; j++) {
				let date = last7Days[j];
				if(date in input) {
					let today_data = input[date]['time'];
					
					if( golden_cases[i] in today_data ) {
						content += "<td>" + today_data[golden_cases[i]] + "</td>";
					} else {
						content += "<td></td>";
					}
				} else {
					content += "<td></td>";
				}
			}
			content += "</tr>";
		}
		
		document.getElementById("main").innerHTML = content;
	}

	var outputMissingDatasetImgs = function() {
		let content = "";
		for (let i = 0; i < 7; i++) {
			if( last7Days[i] in input) {
				// Adding missing cases
				let date = last7Days[i];
				let today_data = input[date];
				content += "<p style='font-weight:bold; font-size:32px;'>" + date + ": ";
				if ( today_data['missing'] == "") {
					content += "no missing cases";
				} else {
					content += "missing cases:<br/>" + today_data['missing'];
				}
				content += "</p>";
				
				//Adding start & end image pairs
				content += "<div onclick='switchDisplay(\"table" + date + "\")'>Click Here to Show/Hide Images</div>"
				content += "<table id='table" + date + "' style='display:none;'><thead><tr><th style='text-align:center;'>Start</th><th style='text-align:center;'>End</th></tr></thead><tbody class=table-hover'>";
				all_cases = Object.keys(today_data['detail']);
			    for (let j = 0; j < all_cases.length; j++) {
					//console.log(all_cases[j]);
					let start = "/" + today_data['detail'][all_cases[j]][0]["file"].split("\\").splice(-5, 5).join("/");
					let end = "/" + today_data['detail'][all_cases[j]][1]["file"].split("\\").splice(-5, 5).join("/");
					content += "<tr>"
					content += "<td>" + all_cases[j] + "<br /><a href='" + start + "' target='_blank'><img src='" + start + "' height='410' width='480' onmouseover= 'this.width=960;this.height=820;' onmouseout='this.width=480;this.height=410;'></a></td>"
					content += "<td>" + all_cases[j] + "<br /><a href='" + end + "' target='_blank'><img src='" + end + "' height='410' width='480'  onmouseover= 'this.width=960;this.height=820;' onmouseout='this.width=480;this.height=410;'></a></td>"
					content += "</tr>"
				}
				content += "</tbody></table>";
			}
		}
		document.getElementById("note").innerHTML = content;
	}
	
	generateTableNumTable();
	outputMissingDatasetImgs();
});

