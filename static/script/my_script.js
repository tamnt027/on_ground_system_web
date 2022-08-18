
const charts = []
const info_charts = []

let refresh_interval_handle;





function update_chart_data(chart, chart_info) {

    chart_id = chart_info.id;

    const time_range = document.getElementById("timerange")
    let period = time_range.selectedOptions[0].getAttribute('data-period')
    const request = new XMLHttpRequest();
    request.open('GET', `/api/charts/${chart_id}/data?timerange=${time_range.value}&period=${period}`)


    request.onload = () => {
        const chart_data = JSON.parse(request.responseText);
        if (chart_data.status == 'success') {

            chart.data.datasets[0].data = []
            for (let i = 0; i < chart_data.sensor.values.length; i++){
                 chart.data.datasets[0].data.push({x: new Date(chart_data.sensor.timestamps[i]), 
                                                  y : chart_data.sensor.values[i]})
            }

            if (chart_data.secondary == 'true'){
                chart.data.datasets[1].data = []
                for (let i = 0; i < chart_data.secondary_sensor.values.length; i++){
                     chart.data.datasets[1].data.push({x: new Date(chart_data.secondary_sensor.timestamps[i]), 
                                                      y : chart_data.secondary_sensor.values[i]})
                }
            }

            chart.update();

        }
    }


    request.send();
}

function creating_chart(chart_id, chart_canvas) {

    const request = new XMLHttpRequest();
    request.open('GET', `/api/charts/${chart_id}`)

    request.onload = () => {
        let chart_info = JSON.parse(request.responseText);
        if (chart_info.status == 'success') {
                        
            let data =  {
                datasets: []
            }

            data.datasets.push({label: chart_info.sensor.name,
                                data : [],
                                yAxisID: 'left-axis',
                                backgroundColor: chart_info.background_color0 + '40'});

            if (chart_info.secondary == 'true'){
                data.datasets.push({label: chart_info.secondary_sensor.name,
                                    data : [],
                                    backgroundColor: chart_info.background_color1 + '40' ,
                                    yAxisID: 'right-axis'});
            }

            let options;
            if (chart_info.secondary == 'false'){
                options = {
                    title: {
                        display: true,
                        text: chart_info.title,
                        fontSize : 20,
                    }, 
                    layout: {
                        padding: {
                            left: 50,
                            right: 0,
                            top: 0,
                            bottom: 0
                        }
                    },
                    scales: {
                        xAxes: [{
                            type: 'time',
                            time: {
                                unit: 'minute',
                                displayFormats: {
                                    minute: 'hh:mm'
                                }
                            },
                            gridLines: {
                                display:false
                            },
                            ticks : {
                                source:'data',
                                
                            },
                            
                        }],

                        yAxes: [{
                                id: 'left-axis',
                                type: 'linear',
                                position: 'left'
                            }
                        ]
            
                    }
                    
                }
            }else{

                options = {
                    title: {
                        display: true,
                        text: chart_info.title,
                        fontSize : 20,
                    },
                    layout: {
                        padding: {
                            left: 50,
                            right: 0,
                            top: 0,
                            bottom: 0
                        }
                    },
                    scales: {
                        xAxes: [{
                            type: 'time',
                            time: {
                                unit: 'minute',
                                displayFormats: {
                                    minute: 'hh:mm'
                                }
                            },
                            gridLines: {
                                display:false
                            },
                            ticks : {
                                source:'data'
                            }
                        }],

                        yAxes: [{
                                id: 'left-axis',
                                type: 'linear',
                                position: 'left'
                            }, {
                                id: 'right-axis',
                                type: 'linear',
                                position: 'right'
                            }
                        ]
            
                    }
                    
                }
            }
    
            let chart = new Chart(chart_canvas, {
                type: 'line',
                data: data,
                options: options
            });

            charts.push(chart); 
            info_charts.push(chart_info)
            update_chart_data(chart, chart_info);
        }
    }
    request.send();
};

function setup_charts() {

    const chart_canvases = document.getElementsByClassName("chart-canvas");

    for (let chart_canvas of chart_canvases)
    {
        let chart_id = chart_canvas.dataset.chartId;
        creating_chart(chart_id, chart_canvas);
    }

};


function refresh_charts(){
    for (let i = 0; i < charts.length; i++) {
        update_chart_data(charts[i], info_charts[i])
    }
}

function refresh_interval_change() {
    clearInterval(refresh_interval_handle);
    const refresh_interval = document.getElementById("refresh-interval")
    refresh_interval_handle = setInterval(refresh_charts, refresh_interval.value  * 1000);
    
}

document.addEventListener('DOMContentLoaded', () => {
    setup_charts();
    const refresh_interval = document.getElementById("refresh-interval")
    refresh_interval_handle = setInterval(refresh_charts, refresh_interval.value  * 1000);
    refresh_interval.addEventListener("change", refresh_interval_change);

    const timerange = document.getElementById("timerange")
    timerange.addEventListener("change", refresh_charts);
});
