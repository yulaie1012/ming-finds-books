var item_status = '一般圖書';

if (item_status == '指定工具書') {
    item_status = '不可外借';
} else if (item_status == '地圖') {
    item_status = '不可外借';
} else if (item_status == '期刊') {
    item_status = '不可外借';
} else if (item_status == '參考書') {
    item_status = '不可外借';
} else if (item_status == '特藏') {
    item_status = '不可外借';
} else if (item_status == '指定參考書') {
    item_status = '不可外借';
} else if (item_status == '教師著作') {
    item_status = '不可外借';
} else if (item_status == '博碩論文') {
    item_status = '不可外借';
} else {
    item_status = '仍在館內';
}
document.write(item_status); 仍在館內
