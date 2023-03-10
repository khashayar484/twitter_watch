
function Update(user) {
    $.ajax({
          data : {
              user : user
          },
          type : "POST",
          url : "/accounts"
      
          }).done(function (data) {
              var active_accounts = data['active_accounts']
              var numbers = data['numbers']
  
              var high_active_user = data['high_active_user']
              var high_active_num = data['high_active_num']
  
              pie_plot(values = active_accounts, label = numbers, id  = "active_account_id" , title = "account contribution" , type = 'pie')
              pie_plot(values = high_active_num, label = high_active_user, id  = "high_active_id" , title = "high active accounts" , type = 'pie')
              
          })
    }
  
  function create_table(id, dates , convs){
      const table = document.createElement("table")
      const thead = document.createElement("thead")
      const tr = document.createElement("tr")
  
      const h1 = document.createElement("th")
      h1.innerText  = "Date"
      
      const h2 = document.createElement("th")
      h2.innerText  = "Conversation"
  
      tr.appendChild(h1, h2)
      thead.appendChild(tr)
      table.appendChild(thead)
  
      var div = document.getElementById(id)
      table.append(thead)
      
      const tbody = document.createElement("tboody")
      table.appendChild(tbody)
      
      for (let index = 0; index < dates.length; index++) {
        const date = dates[index];
        const conv = convs[index]
        const tr = document.createElement("tr")
        const tdforDame =  document.createElement("td")
        tdforDame.innerText = date
        tr.appendChild(tdforDame)
  
        const tdforConv =  document.createElement("td")
        tdforConv.innerText = conv
        tr.appendChild(tdforConv)
  
        tbody.appendChild(tr)
      }
      div.appendChild(table)
    }
    
  function Tweets() {
      $.ajax({
          type : "POST",
          url : "/tweets"
        }).done(function(data){
          create_table("tweet_id" , data['date'] , data['conversations'])
        })
    }
  
  function Replies() {
    $.ajax({
          type : "POST",
          url : "/replies"
        }).done(function(data){
          create_table("reply_id" , data['date'] , data['conversations'])
        })
    }
  
  function Sentiment() {
    $.ajax({
        type : "POST",
        url : '/sentiment/tweets'
      }).done(function(data){
        timeseries_plot(data['date_range'], data['sentiments'], data['names'], "sentiment_id_tweets" , "Tweet Sentiment")
      })
  
      $.ajax({
        type : "POST",
        url : '/sentiment/replies'
      }).done(function(data){
        timeseries_plot(data['date_range'], data['sentiments'], data['names'], "sentiment_id_replies" , "Reply Sentiment")
      })
  }
  
  function timeseries_plot(dates, data, name, id , title_text) {
    var list_dates = []
    var datas = []
    var traces = []
  
    for (let index = 0; index < dates.length; index++) {
        list_dates.push(dates[index])
    }
  
    for (let columns = 0; columns < name.length; columns++) {
          var one_data = []
          for (let index = 0; index < data.length; index++) {
              one_data.push(data[index][columns])
          }
          var trace = {
              name : name[columns],
              x : list_dates,
              y : one_data,
              type : "scatter",
          }
          traces.push(trace)   
      }
  
        var layout = {
            xaxis : {
                showgrid: false,
                tickcolor: '#000',
                // title: 'Time',
                titlefont: {color: "rgb(252, 250, 250)",
                            family: 'Times New Roman',
                            size: 20},
                            color : "rrgb(252, 250, 250)"
            },
            yaxis :{
                showgrid: false,
                tickcolor: '#000',
                title: 'Value',
                titlefont: {color: "rgb(252, 250, 250)",
                            family: 'Times New Roman',
                            size: 20},
                color : "white"
            },
            title: {
                text : title_text, 
                font: {
                family: 'Times New Roman',
                size: 20,
                color: 'rgb(252, 250, 250)',
                },
                },
                showlegend: true,
                legend: {
                    font: {
                    family: 'Times New Roman',
                    size: 15,
                    color: 'rgb(252, 250, 250)'
                    },
                },
                height: 450,
                width: 1100,
                paper_bgcolor: 'rgba(0,0,0,0)',
                plot_bgcolor : 'rgba(0,0,0,0)'
        }
  
    canvas = document.getElementById(id)
    Plotly.newPlot(canvas, traces, layout) // ,{staticPlot: true},{scrollZoom: true}
  
  }
  
  function pie_plot(values, label, id, title , type) {
    var data = [{
    values : values,
    labels : label,
    type : type,
    marker: {
      color: '#e9e9e9'
    }
    }]
  
    var layout = {
      autosize: false,
      title: {
      text:`${title}`,
      font: {
        family: 'Times New Roman',
        size: 20,
        color: 'rgb(255, 255, 255)',
      },
      xref: 'paper',
      x: 0.05,
      },
      margin: {
      l: 20,
      r: 5,
      },
      showlegend: true,
      legend: {
      traceorder: 'normal',
      x: -5,
      xanchor: 'right',
      y: 1,
      font: {
        family: 'sans-serif',
        size: 10,
        color: 'rgb(255, 255, 255)'
      },
      // bgcolor: '#E2E2E2',
      // bordercolor: '#FFFFFF',
      // borderwidth: 2
      },
      height: 400,
      width: 450,
      paper_bgcolor: 'rgba(0,0,0,0)',
      plot_bgcolor : 'rgba(0,0,0,0)'
  
    };
    Plotly.newPlot( `${id}`, data, layout);
  }
  