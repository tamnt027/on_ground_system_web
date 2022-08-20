
const current_all_charts = []

let refresh_interval_handle;


const config = {
    displayModeBar: true, // this is the line that hides the bar.
  };

function refresh_single_chart(chart_canvas) {

    let chart_id = chart_canvas.dataset.chartId;
    const time_range = document.getElementById("timerange")
    let period = time_range.selectedOptions[0].getAttribute('data-period')
    const request = new XMLHttpRequest();
    request.open('GET', `/api/charts/${chart_id}?timerange=${time_range.value}&period=${period}`)

    request.onload = () => {
        const chart_data = JSON.parse(request.responseText);
        if (chart_data.status == 'success') {
            let chart_name_id = chart_canvas.id;
            Plotly.newPlot(chart_name_id, chart_data.data,  chart_data.layout );

        }
    }


    request.send();
}


function setup_charts() {

    const chart_canvases = document.getElementsByClassName("chart-canvas");

    for (let chart_canvas of chart_canvases)
    {
        let chart_name_id = chart_canvas.id;
        let chart_id = chart_canvas.dataset.chartId;

        const time_range = document.getElementById("timerange")
        let period = time_range.selectedOptions[0].getAttribute('data-period')
        const request = new XMLHttpRequest();
        request.open('GET', `/api/charts/${chart_id}?timerange=${time_range.value}&period=${period}`)


        request.onload = () => {
            let chart_info = JSON.parse(request.responseText);
            if (chart_info.status == 'success') {

                let data = chart_info.data;
                let layout = chart_info.layout;


                Plotly.newPlot(chart_name_id, data, layout, config);
                current_all_charts.push(chart_name_id)
            }
        }
        request.send();
    }

};


function refresh_all_charts(){
    const chart_canvases = document.getElementsByClassName("chart-canvas");
    for (let chart_canvas of chart_canvases)
    {
        refresh_single_chart(chart_canvas);
    }
  
}

function refresh_interval_change() {
    clearInterval(refresh_interval_handle);
    const refresh_interval = document.getElementById("refresh-interval")
    refresh_interval_handle = setInterval(refresh_all_charts, refresh_interval.value  * 1000);
    
}

document.addEventListener('DOMContentLoaded', () => {
    setup_charts();
    const refresh_interval = document.getElementById("refresh-interval")
    refresh_interval_handle = setInterval(refresh_all_charts, refresh_interval.value  * 1000);
    refresh_interval.addEventListener("change", refresh_interval_change);

    const timerange = document.getElementById("timerange")
    timerange.addEventListener("change", refresh_all_charts);
});
