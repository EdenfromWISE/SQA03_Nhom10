/*
   Licensed to the Apache Software Foundation (ASF) under one or more
   contributor license agreements.  See the NOTICE file distributed with
   this work for additional information regarding copyright ownership.
   The ASF licenses this file to You under the Apache License, Version 2.0
   (the "License"); you may not use this file except in compliance with
   the License.  You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.
*/
var showControllersOnly = false;
var seriesFilter = "";
var filtersOnlySampleSeries = true;

/*
 * Add header in statistics table to group metrics by category
 * format
 *
 */
function summaryTableHeader(header) {
    var newRow = header.insertRow(-1);
    newRow.className = "tablesorter-no-sort";
    var cell = document.createElement('th');
    cell.setAttribute("data-sorter", false);
    cell.colSpan = 1;
    cell.innerHTML = "Requests";
    newRow.appendChild(cell);

    cell = document.createElement('th');
    cell.setAttribute("data-sorter", false);
    cell.colSpan = 3;
    cell.innerHTML = "Executions";
    newRow.appendChild(cell);

    cell = document.createElement('th');
    cell.setAttribute("data-sorter", false);
    cell.colSpan = 7;
    cell.innerHTML = "Response Times (ms)";
    newRow.appendChild(cell);

    cell = document.createElement('th');
    cell.setAttribute("data-sorter", false);
    cell.colSpan = 1;
    cell.innerHTML = "Throughput";
    newRow.appendChild(cell);

    cell = document.createElement('th');
    cell.setAttribute("data-sorter", false);
    cell.colSpan = 2;
    cell.innerHTML = "Network (KB/sec)";
    newRow.appendChild(cell);
}

/*
 * Populates the table identified by id parameter with the specified data and
 * format
 *
 */
function createTable(table, info, formatter, defaultSorts, seriesIndex, headerCreator) {
    var tableRef = table[0];

    // Create header and populate it with data.titles array
    var header = tableRef.createTHead();

    // Call callback is available
    if(headerCreator) {
        headerCreator(header);
    }

    var newRow = header.insertRow(-1);
    for (var index = 0; index < info.titles.length; index++) {
        var cell = document.createElement('th');
        cell.innerHTML = info.titles[index];
        newRow.appendChild(cell);
    }

    var tBody;

    // Create overall body if defined
    if(info.overall){
        tBody = document.createElement('tbody');
        tBody.className = "tablesorter-no-sort";
        tableRef.appendChild(tBody);
        var newRow = tBody.insertRow(-1);
        var data = info.overall.data;
        for(var index=0;index < data.length; index++){
            var cell = newRow.insertCell(-1);
            cell.innerHTML = formatter ? formatter(index, data[index]): data[index];
        }
    }

    // Create regular body
    tBody = document.createElement('tbody');
    tableRef.appendChild(tBody);

    var regexp;
    if(seriesFilter) {
        regexp = new RegExp(seriesFilter, 'i');
    }
    // Populate body with data.items array
    for(var index=0; index < info.items.length; index++){
        var item = info.items[index];
        if((!regexp || filtersOnlySampleSeries && !info.supportsControllersDiscrimination || regexp.test(item.data[seriesIndex]))
                &&
                (!showControllersOnly || !info.supportsControllersDiscrimination || item.isController)){
            if(item.data.length > 0) {
                var newRow = tBody.insertRow(-1);
                for(var col=0; col < item.data.length; col++){
                    var cell = newRow.insertCell(-1);
                    cell.innerHTML = formatter ? formatter(col, item.data[col]) : item.data[col];
                }
            }
        }
    }

    // Add support of columns sort
    table.tablesorter({sortList : defaultSorts});
}

$(document).ready(function() {

    // Customize table sorter default options
    $.extend( $.tablesorter.defaults, {
        theme: 'blue',
        cssInfoBlock: "tablesorter-no-sort",
        widthFixed: true,
        widgets: ['zebra']
    });

    var data = {"OkPercent": 99.89444620367438, "KoPercent": 0.10555379632561679};
    var dataset = [
        {
            "label" : "FAIL",
            "data" : data.KoPercent,
            "color" : "#FF6347"
        },
        {
            "label" : "PASS",
            "data" : data.OkPercent,
            "color" : "#9ACD32"
        }];
    $.plot($("#flot-requests-summary"), dataset, {
        series : {
            pie : {
                show : true,
                radius : 1,
                label : {
                    show : true,
                    radius : 3 / 4,
                    formatter : function(label, series) {
                        return '<div style="font-size:8pt;text-align:center;padding:2px;color:white;">'
                            + label
                            + '<br/>'
                            + Math.round10(series.percent, -2)
                            + '%</div>';
                    },
                    background : {
                        opacity : 0.5,
                        color : '#000'
                    }
                }
            }
        },
        legend : {
            show : true
        }
    });

    // Creates APDEX table
    createTable($("#apdexTable"), {"supportsControllersDiscrimination": true, "overall": {"data": [0.9988861296756165, 500, 1500, "Total"], "isController": false}, "titles": ["Apdex", "T (Toleration threshold)", "F (Frustration threshold)", "Label"], "items": [{"data": [0.9982129180495277, 500, 1500, "08-Session-Submit-Answer"], "isController": false}, {"data": [0.999231852515683, 500, 1500, "21-Progress-Overview"], "isController": false}, {"data": [0.9982136021436774, 500, 1500, "06-Session-Get-Info"], "isController": false}, {"data": [0.9989806320081549, 500, 1500, "03-Vocab-Course-Detail"], "isController": false}, {"data": [0.9997452553814801, 500, 1500, "02-Vocab-List-Courses"], "isController": false}, {"data": [0.9985931704821589, 500, 1500, "16-Exam-Complete"], "isController": false}, {"data": [0.9993604502430289, 500, 1500, "17-History-All"], "isController": false}, {"data": [0.9991041719989762, 500, 1500, "20-Progress-Upcoming-Review"], "isController": false}, {"data": [0.9988476312419975, 500, 1500, "22-Progress-Daily"], "isController": false}, {"data": [0.9987228607918263, 500, 1500, "09-Session-Complete"], "isController": false}, {"data": [0.9989790709545686, 500, 1500, "07-Session-Get-Questions"], "isController": false}, {"data": [0.9988485158648925, 500, 1500, "18-History-Practice"], "isController": false}, {"data": [0.9984631147540983, 500, 1500, "24-Chatbot-Send-Message"], "isController": false}, {"data": [0.9993597951344431, 500, 1500, "23-Progress-Recent-Sessions"], "isController": false}, {"data": [0.9992331288343558, 500, 1500, "13-Session-Create-Exam"], "isController": false}, {"data": [0.9991044012282497, 500, 1500, "19-Progress-Streak"], "isController": false}, {"data": [0.9994875080076874, 500, 1500, "25-Chatbot-Get-History"], "isController": false}, {"data": [0.9976982097186701, 500, 1500, "15-Exam-Submit-Answer"], "isController": false}, {"data": [0.9985947879407256, 500, 1500, "10-Session-Get-Detail"], "isController": false}, {"data": [0.9983382334142912, 500, 1500, "14-Exam-Get-Questions"], "isController": false}, {"data": [0.9994902510513572, 500, 1500, "04-Vocab-Topic-Detail"], "isController": false}, {"data": [0.9984084542908073, 500, 1500, "01-Auth-Login"], "isController": false}, {"data": [0.9993625701172871, 500, 1500, "05-Session-Create-Practice"], "isController": false}]}, function(index, item){
        switch(index){
            case 0:
                item = item.toFixed(3);
                break;
            case 1:
            case 2:
                item = formatDuration(item);
                break;
        }
        return item;
    }, [[0, 0]], 3);

    // Create statistics table
    createTable($("#statisticsTable"), {"supportsControllersDiscrimination": true, "overall": {"data": ["Total", 360006, 380, 0.10555379632561679, 27.36509391510122, 0, 849, 16.0, 35.0, 148.95000000000073, 291.9900000000016, 100.00913957181801, 509.143154985053, 45.252406425473175], "isController": false}, "titles": ["Label", "#Samples", "FAIL", "Error %", "Average", "Min", "Max", "Median", "90th pct", "95th pct", "99th pct", "Transactions/s", "Received", "Sent"], "items": [{"data": ["08-Session-Submit-Answer", 15668, 28, 0.17870819504723, 15.409241766658171, 0, 333, 13.0, 20.0, 24.0, 33.0, 4.353478684542567, 1.9595314713746552, 2.3445731542381263], "isController": false}, {"data": ["21-Progress-Overview", 15622, 12, 0.07681474843169889, 11.457047753168627, 0, 281, 10.0, 15.0, 18.0, 26.770000000000437, 4.341965196461279, 2.0014391818792023, 1.894756152703931], "isController": false}, {"data": ["06-Session-Get-Info", 15674, 28, 0.17863978563225724, 9.56896771723872, 0, 290, 8.0, 13.0, 15.0, 23.0, 4.355448381378777, 2.634876809015784, 1.9219414170101463], "isController": false}, {"data": ["03-Vocab-Course-Detail", 15696, 16, 0.1019367991845056, 10.594801223241593, 0, 312, 9.0, 13.0, 16.0, 24.0, 4.361021205799025, 21.796209631519268, 1.915358995002163], "isController": false}, {"data": ["02-Vocab-List-Courses", 15702, 4, 0.025474461851993375, 22.489237039867447, 5, 348, 20.0, 29.0, 34.0, 46.0, 4.362564627885907, 199.00045202880648, 1.9089828845673513], "isController": false}, {"data": ["16-Exam-Complete", 15638, 22, 0.1406829517841156, 30.35349788975561, 0, 368, 28.0, 38.0, 43.0, 60.61000000000058, 4.346240688016738, 2.052750848757883, 2.0418752807074494], "isController": false}, {"data": ["17-History-All", 15636, 10, 0.06395497569710923, 21.957917625991257, 1, 349, 19.0, 29.0, 34.0, 50.0, 4.345143809920801, 25.414977052070306, 1.9303198164165625], "isController": false}, {"data": ["20-Progress-Upcoming-Review", 15628, 14, 0.08958280010238034, 11.641028922446859, 0, 288, 10.0, 15.0, 18.0, 25.0, 4.343195845116767, 4.145798034271729, 1.9543924269413206], "isController": false}, {"data": ["22-Progress-Daily", 15620, 18, 0.11523687580025609, 14.886811779769529, 0, 297, 13.0, 19.0, 22.0, 32.0, 4.343221252087846, 2.2175179637521762, 1.9200005955593482], "isController": false}, {"data": ["09-Session-Complete", 15660, 20, 0.1277139208173691, 29.316985951468588, 0, 381, 27.0, 38.0, 44.0, 59.0, 4.351265493047561, 2.050895948071564, 2.044221915026398], "isController": false}, {"data": ["07-Session-Get-Questions", 15672, 16, 0.10209290454313426, 11.399693721286287, 1, 281, 10.0, 15.0, 17.0, 26.0, 4.354412259926627, 25.641799431623056, 1.965463126558025], "isController": false}, {"data": ["18-History-Practice", 15632, 18, 0.11514841351074719, 15.700230296827035, 0, 336, 14.0, 21.0, 25.0, 36.0, 4.345530861136216, 13.51783138912155, 2.0270207816562555], "isController": false}, {"data": ["24-Chatbot-Send-Message", 15616, 24, 0.15368852459016394, 22.675076844262183, 0, 398, 20.0, 30.0, 35.0, 53.0, 4.34053884276387, 1.8303635333309243, 2.023912216034644], "isController": false}, {"data": ["23-Progress-Recent-Sessions", 15620, 10, 0.06402048655569782, 9.627016645326588, 0, 241, 9.0, 13.0, 15.0, 22.0, 4.34209600924683, 5.572347134313929, 1.9247267460882913], "isController": false}, {"data": ["13-Session-Create-Exam", 15648, 12, 0.07668711656441718, 21.8833077709612, 0, 350, 20.0, 28.0, 31.0, 42.0, 4.348199406957619, 2.2563547183368247, 2.326133547144813], "isController": false}, {"data": ["19-Progress-Streak", 15632, 14, 0.08955987717502559, 9.890736949846511, 0, 310, 8.0, 13.0, 15.0, 24.0, 4.344352161545869, 6.738776420071229, 1.8870759075282741], "isController": false}, {"data": ["25-Chatbot-Get-History", 15610, 8, 0.05124919923126201, 11.268417680973725, 1, 305, 10.0, 15.0, 17.0, 24.889999999999418, 4.339532108923646, 64.222505369337, 1.8518119501220685], "isController": false}, {"data": ["15-Exam-Submit-Answer", 15640, 36, 0.23017902813299232, 15.220843989769776, 1, 320, 13.0, 20.0, 23.0, 34.0, 4.346738556460354, 1.9612613471345988, 2.3412492226800254], "isController": false}, {"data": ["10-Session-Get-Detail", 15656, 22, 0.14052120592743997, 15.321410321921373, 1, 303, 14.0, 19.0, 22.0, 32.0, 4.350822587816808, 65.6079383805997, 1.950349243761116], "isController": false}, {"data": ["14-Exam-Get-Questions", 15646, 26, 0.16617665857088074, 11.046018151604244, 0, 298, 10.0, 14.0, 17.0, 26.0, 4.3476364068838596, 14.642670774149375, 1.9614134981592153], "isController": false}, {"data": ["04-Vocab-Topic-Detail", 15694, 8, 0.05097489486427934, 10.77188734548233, 0, 352, 9.0, 14.0, 17.0, 26.0, 4.36036738887509, 36.51567348682555, 1.9117902959598672], "isController": false}, {"data": ["01-Auth-Login", 15708, 4, 0.02546473134708429, 276.22396231219744, 1, 849, 270.0, 298.0, 311.0, 358.0, 4.363907914542081, 5.371949711225867, 1.1282757264428707], "isController": false}, {"data": ["05-Session-Create-Practice", 15688, 10, 0.06374298827129016, 19.759688934217273, 1, 313, 18.0, 25.0, 29.0, 38.0, 4.358814206933649, 2.1373544610537953, 2.093829571871812], "isController": false}]}, function(index, item){
        switch(index){
            // Errors pct
            case 3:
                item = item.toFixed(2) + '%';
                break;
            // Mean
            case 4:
            // Mean
            case 7:
            // Median
            case 8:
            // Percentile 1
            case 9:
            // Percentile 2
            case 10:
            // Percentile 3
            case 11:
            // Throughput
            case 12:
            // Kbytes/s
            case 13:
            // Sent Kbytes/s
                item = item.toFixed(2);
                break;
        }
        return item;
    }, [[0, 0]], 0, summaryTableHeader);

    // Create error table
    createTable($("#errorsTable"), {"supportsControllersDiscrimination": false, "titles": ["Type of error", "Number of errors", "% in errors", "% in all samples"], "items": [{"data": ["500/Internal Server Error", 20, 5.2631578947368425, 0.005555462964506147], "isController": false}, {"data": ["Non HTTP response code: java.net.BindException/Non HTTP response message: Address already in use: connect", 2, 0.5263157894736842, 5.555462964506147E-4], "isController": false}, {"data": ["401/Unauthorized", 88, 23.157894736842106, 0.024444037043827048], "isController": false}, {"data": ["Non HTTP response code: org.apache.http.conn.HttpHostConnectException/Non HTTP response message: Connect to 127.0.0.1:8000 [/127.0.0.1] failed: Connection refused: connect", 216, 56.8421052631579, 0.05999900001666639], "isController": false}, {"data": ["404/Not Found", 54, 14.210526315789474, 0.014999750004166597], "isController": false}]}, function(index, item){
        switch(index){
            case 2:
            case 3:
                item = item.toFixed(2) + '%';
                break;
        }
        return item;
    }, [[1, 1]]);

        // Create top5 errors by sampler
    createTable($("#top5ErrorsBySamplerTable"), {"supportsControllersDiscrimination": false, "overall": {"data": ["Total", 360006, 380, "Non HTTP response code: org.apache.http.conn.HttpHostConnectException/Non HTTP response message: Connect to 127.0.0.1:8000 [/127.0.0.1] failed: Connection refused: connect", 216, "401/Unauthorized", 88, "404/Not Found", 54, "500/Internal Server Error", 20, "Non HTTP response code: java.net.BindException/Non HTTP response message: Address already in use: connect", 2], "isController": false}, "titles": ["Sample", "#Samples", "#Errors", "Error", "#Errors", "Error", "#Errors", "Error", "#Errors", "Error", "#Errors", "Error", "#Errors"], "items": [{"data": ["08-Session-Submit-Answer", 15668, 28, "Non HTTP response code: org.apache.http.conn.HttpHostConnectException/Non HTTP response message: Connect to 127.0.0.1:8000 [/127.0.0.1] failed: Connection refused: connect", 12, "500/Internal Server Error", 6, "404/Not Found", 6, "401/Unauthorized", 4, "", ""], "isController": false}, {"data": ["21-Progress-Overview", 15622, 12, "Non HTTP response code: org.apache.http.conn.HttpHostConnectException/Non HTTP response message: Connect to 127.0.0.1:8000 [/127.0.0.1] failed: Connection refused: connect", 8, "401/Unauthorized", 4, "", "", "", "", "", ""], "isController": false}, {"data": ["06-Session-Get-Info", 15674, 28, "Non HTTP response code: org.apache.http.conn.HttpHostConnectException/Non HTTP response message: Connect to 127.0.0.1:8000 [/127.0.0.1] failed: Connection refused: connect", 18, "404/Not Found", 6, "401/Unauthorized", 4, "", "", "", ""], "isController": false}, {"data": ["03-Vocab-Course-Detail", 15696, 16, "Non HTTP response code: org.apache.http.conn.HttpHostConnectException/Non HTTP response message: Connect to 127.0.0.1:8000 [/127.0.0.1] failed: Connection refused: connect", 12, "401/Unauthorized", 4, "", "", "", "", "", ""], "isController": false}, {"data": ["02-Vocab-List-Courses", 15702, 4, "401/Unauthorized", 4, "", "", "", "", "", "", "", ""], "isController": false}, {"data": ["16-Exam-Complete", 15638, 22, "Non HTTP response code: org.apache.http.conn.HttpHostConnectException/Non HTTP response message: Connect to 127.0.0.1:8000 [/127.0.0.1] failed: Connection refused: connect", 10, "404/Not Found", 8, "401/Unauthorized", 4, "", "", "", ""], "isController": false}, {"data": ["17-History-All", 15636, 10, "Non HTTP response code: org.apache.http.conn.HttpHostConnectException/Non HTTP response message: Connect to 127.0.0.1:8000 [/127.0.0.1] failed: Connection refused: connect", 6, "401/Unauthorized", 4, "", "", "", "", "", ""], "isController": false}, {"data": ["20-Progress-Upcoming-Review", 15628, 14, "Non HTTP response code: org.apache.http.conn.HttpHostConnectException/Non HTTP response message: Connect to 127.0.0.1:8000 [/127.0.0.1] failed: Connection refused: connect", 8, "401/Unauthorized", 4, "Non HTTP response code: java.net.BindException/Non HTTP response message: Address already in use: connect", 2, "", "", "", ""], "isController": false}, {"data": ["22-Progress-Daily", 15620, 18, "Non HTTP response code: org.apache.http.conn.HttpHostConnectException/Non HTTP response message: Connect to 127.0.0.1:8000 [/127.0.0.1] failed: Connection refused: connect", 14, "401/Unauthorized", 4, "", "", "", "", "", ""], "isController": false}, {"data": ["09-Session-Complete", 15660, 20, "Non HTTP response code: org.apache.http.conn.HttpHostConnectException/Non HTTP response message: Connect to 127.0.0.1:8000 [/127.0.0.1] failed: Connection refused: connect", 10, "404/Not Found", 6, "401/Unauthorized", 4, "", "", "", ""], "isController": false}, {"data": ["07-Session-Get-Questions", 15672, 16, "404/Not Found", 6, "Non HTTP response code: org.apache.http.conn.HttpHostConnectException/Non HTTP response message: Connect to 127.0.0.1:8000 [/127.0.0.1] failed: Connection refused: connect", 6, "401/Unauthorized", 4, "", "", "", ""], "isController": false}, {"data": ["18-History-Practice", 15632, 18, "Non HTTP response code: org.apache.http.conn.HttpHostConnectException/Non HTTP response message: Connect to 127.0.0.1:8000 [/127.0.0.1] failed: Connection refused: connect", 14, "401/Unauthorized", 4, "", "", "", "", "", ""], "isController": false}, {"data": ["24-Chatbot-Send-Message", 15616, 24, "Non HTTP response code: org.apache.http.conn.HttpHostConnectException/Non HTTP response message: Connect to 127.0.0.1:8000 [/127.0.0.1] failed: Connection refused: connect", 20, "401/Unauthorized", 4, "", "", "", "", "", ""], "isController": false}, {"data": ["23-Progress-Recent-Sessions", 15620, 10, "Non HTTP response code: org.apache.http.conn.HttpHostConnectException/Non HTTP response message: Connect to 127.0.0.1:8000 [/127.0.0.1] failed: Connection refused: connect", 6, "401/Unauthorized", 4, "", "", "", "", "", ""], "isController": false}, {"data": ["13-Session-Create-Exam", 15648, 12, "Non HTTP response code: org.apache.http.conn.HttpHostConnectException/Non HTTP response message: Connect to 127.0.0.1:8000 [/127.0.0.1] failed: Connection refused: connect", 8, "401/Unauthorized", 4, "", "", "", "", "", ""], "isController": false}, {"data": ["19-Progress-Streak", 15632, 14, "Non HTTP response code: org.apache.http.conn.HttpHostConnectException/Non HTTP response message: Connect to 127.0.0.1:8000 [/127.0.0.1] failed: Connection refused: connect", 10, "401/Unauthorized", 4, "", "", "", "", "", ""], "isController": false}, {"data": ["25-Chatbot-Get-History", 15610, 8, "401/Unauthorized", 4, "Non HTTP response code: org.apache.http.conn.HttpHostConnectException/Non HTTP response message: Connect to 127.0.0.1:8000 [/127.0.0.1] failed: Connection refused: connect", 4, "", "", "", "", "", ""], "isController": false}, {"data": ["15-Exam-Submit-Answer", 15640, 36, "500/Internal Server Error", 14, "Non HTTP response code: org.apache.http.conn.HttpHostConnectException/Non HTTP response message: Connect to 127.0.0.1:8000 [/127.0.0.1] failed: Connection refused: connect", 10, "404/Not Found", 8, "401/Unauthorized", 4, "", ""], "isController": false}, {"data": ["10-Session-Get-Detail", 15656, 22, "Non HTTP response code: org.apache.http.conn.HttpHostConnectException/Non HTTP response message: Connect to 127.0.0.1:8000 [/127.0.0.1] failed: Connection refused: connect", 12, "404/Not Found", 6, "401/Unauthorized", 4, "", "", "", ""], "isController": false}, {"data": ["14-Exam-Get-Questions", 15646, 26, "Non HTTP response code: org.apache.http.conn.HttpHostConnectException/Non HTTP response message: Connect to 127.0.0.1:8000 [/127.0.0.1] failed: Connection refused: connect", 14, "404/Not Found", 8, "401/Unauthorized", 4, "", "", "", ""], "isController": false}, {"data": ["04-Vocab-Topic-Detail", 15694, 8, "401/Unauthorized", 4, "Non HTTP response code: org.apache.http.conn.HttpHostConnectException/Non HTTP response message: Connect to 127.0.0.1:8000 [/127.0.0.1] failed: Connection refused: connect", 4, "", "", "", "", "", ""], "isController": false}, {"data": ["01-Auth-Login", 15708, 4, "Non HTTP response code: org.apache.http.conn.HttpHostConnectException/Non HTTP response message: Connect to 127.0.0.1:8000 [/127.0.0.1] failed: Connection refused: connect", 4, "", "", "", "", "", "", "", ""], "isController": false}, {"data": ["05-Session-Create-Practice", 15688, 10, "Non HTTP response code: org.apache.http.conn.HttpHostConnectException/Non HTTP response message: Connect to 127.0.0.1:8000 [/127.0.0.1] failed: Connection refused: connect", 6, "401/Unauthorized", 4, "", "", "", "", "", ""], "isController": false}]}, function(index, item){
        return item;
    }, [[0, 0]], 0);

});
