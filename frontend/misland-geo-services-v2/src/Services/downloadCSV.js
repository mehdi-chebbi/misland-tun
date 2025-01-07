function convertChartDataToCSV(args) {
    let result, ctr, keys, columnDelimiter, lineDelimiter, data;
    data = args.data;
    if (data.length === 0) {
        return null;
    }
    columnDelimiter = args.columnDelimiter || ',';
    lineDelimiter = args.lineDelimiter || '\n';
    keys = Object.keys(data[0]);
    result = '';
    result += keys.join(columnDelimiter);
    result += lineDelimiter;
    
    data.forEach(function (item) {
        ctr = 0;
        keys.forEach(function (key) {
            if (ctr > 0) result += columnDelimiter;
            result += item[key];
            ctr++;
        });
        result += lineDelimiter;
        if(process.env.DEV) console.log("convertChartDataToCSV", result)
    });
    return result;
  }
  
  export function downloadCSV(args) {
    if(process.env.DEV) console.log("download csv data args", args)
    let data, filename, link;
    let csv = "";
    csv += convertChartDataToCSV({
        data: args.data
    });
    if (csv == null) return;
    filename = args.filename || 'chart-data.csv';
    if (!csv.match(/^data:text\/csv/i)) {
        csv = 'data:text/csv;charset=utf-8,' + csv;
    }
    data = encodeURI(csv);
    link = document.createElement('a');
    link.setAttribute('href', data);
    link.setAttribute('download', filename);
    document.body.appendChild(link); // Required for FF
    link.click();
    document.body.removeChild(link);
  }