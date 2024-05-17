var myChart = null;

function renderChart(data) {
  if (myChart instanceof Chart) {
    myChart.destroy();
  }
  var ctx = document.getElementById("myChart").getContext("2d");
  myChart = new Chart(ctx, {
    type: "pie", // 这里改为饼图
    data: {
      labels: Object.keys(data), // 标签组合作为图表的标签
      datasets: [
        {
          label: "标签组合数量",
          data: Object.values(data), // 每个组合的数量
          backgroundColor: [
            "rgba(255, 99, 132, 0.2)",
            "rgba(54, 162, 235, 0.2)",
            "rgba(255, 206, 86, 0.2)",
            "rgba(75, 192, 192, 0.2)",
            "rgba(153, 102, 255, 0.2)",
            "rgba(255, 159, 64, 0.2)",
          ],
          borderColor: [
            "rgba(255, 99, 132, 1)",
            "rgba(54, 162, 235, 1)",
            "rgba(255, 206, 86, 1)",
            "rgba(75, 192, 192, 1)",
            "rgba(153, 102, 255, 1)",
            "rgba(255, 159, 64, 1)",
          ],
          borderWidth: 1,
        },
      ],
    },
    options: {
      scales: {
        y: {
          beginAtZero: true,
        },
      },
    },
  });
}
// 获取文件列表
function getFileList() {
  $.get("/files", function (data) {
    var files = data.files;
    var select = $("#fileSelect");
    select.empty();
    files.forEach(function (file) {
      select.append('<option value="' + file + '">' + file + "</option>");
    });
    layui.form.render("select"); // 更新渲染
  });
}
layui.use(["table", "form", "layer"], function () {
  var table = layui.table;
  var form = layui.form;
  var layer = layui.layer;
  var originalData = []; // 用于存储原始数据
  getFileList(); // 获取文件列表
  // 定义表格的设置
  var tableOptions = {
    elem: "#demo",
    cols: [
      [
        { field: "id", title: "ID" },
        {
          field: "num",
          title: "前提数量",
          sort: true,
        },
        { field: "response", title: "逻辑公式" },
        { field: "label", title: "标签" },
        { field: "label-AI", title: "AI输出标签" },
        {
          field: "same",
          title: "一致",

          templet: function (d) {
            return `<button class="layui-btn layui-btn-xs ${
              d.same ? "layui-btn-normal" : "layui-btn-danger"
            }">${d.same ? "True" : "False"}</button>`;
          },
        },
        { title: "操作", toolbar: "#barDemo" },
      ],
    ],
    page: true,
    limits: [10, 50, 100, 150, 200],
  };

  // 加载数据
  function loadData(data) {
    var filterText = data ? data.search : null;
    var filePath = data ? data.filePath : "res.jsonl";
    var filterSame = data ? data.filterSame : "all"; // 新增筛选参数
    var filterLabel = data ? data.filterLabel : "all"; // 新增筛选参数
    var filterAILabel = data ? data.filterAILabel : "all"; // 新增筛选参数
    $.ajax({
      type: "GET",
      url: "/file/" + filePath, // 你的JSONL文件路径
      dataType: "text",
      success: function (data) {
        // 替换双换行符为单换行符
        data = data.replace(/\n\n/g, "\n");
        var lines = data.trim().split("\n");
        originalData = lines.map(function (line) {
          try {
            var item = JSON.parse(line);
            // 确保num字段是基于premises的长度，并且是数字类型
            item.num = item.premises.length;
            return item;
          } catch (e) {
            console.error("无法解析JSONL数据: " + line);
            return "";
          }
        });
        renderChart(
          originalData.reduce(function (acc, item) {
            var key = item.label + "-" + item["label-AI"];
            acc[key] = (acc[key] || 0) + 1;
            return acc;
          }, {})
        );
        // 计算正确率和错误数量
        var totalCount = originalData.length;
        var trueCount = originalData.filter(function (item) {
          return item.same === true;
        }).length;
        var falseCount = originalData.filter(function (item) {
          return item["label-AI"] === "Error";
        }).length;
        var accuracy = (trueCount / totalCount) * 100;
        $("#accuracy").text(accuracy.toFixed(2) + "%");
        var totalCount = originalData.filter(function (item) {
          return item["label-AI"] !== "Error";
        }).length;
        var accuracy2 = (trueCount / totalCount) * 100;
        $("#accuracy2").text(accuracy2.toFixed(2) + "%");
        var trueCount = originalData.filter(function (item) {
          return item.same === true || (item['label-AI'] == "Error" && item.label == "Unknown");
        }).length;
        var accuracy3 = (trueCount /  originalData.length) * 100;
        $("#accuracy3").text(accuracy3.toFixed(2) + "%");
        $("#errorCount").text(falseCount);
        if (filterText) {
          // 根据搜索内容过滤数据
          tableOptions.data = originalData.filter(function (item) {
            return (
              item["id"] == filterText ||
              item["premises-FOL"].join(" ").includes(filterText) ||
              item.response.join(" ").includes(filterText) ||
              item["conclusion"].includes(filterText) ||
              item["conclusion-FOL"].includes(filterText) ||
              item["premises"].join(" ").includes(filterText)
            );
          });
        } else {
          tableOptions.data = originalData;
        }

        if (filterSame !== "all") {
          // 根据筛选条件进一步过滤数据
          var isSame = filterSame === "true"; // 将筛选值转换为布尔值
          tableOptions.data = tableOptions.data.filter(function (item) {
            return item.same === isSame;
          });
        }
        if (filterLabel !== "all") {
          // 根据筛选条件进一步过滤数据
          tableOptions.data = tableOptions.data.filter(function (item) {
            return item.label === filterLabel;
          });
        }
        if (filterAILabel !== "all") {
          // 根据筛选条件进一步过滤数据
          tableOptions.data = tableOptions.data.filter(function (item) {
            return item["label-AI"] === filterAILabel;
          });
        }
        //打印id构成的数组
        console.log(tableOptions.data.map((item) => item.id));

        table.render(tableOptions);
      },
      error: function () {
        layer.msg("无法加载JSONL数据", { icon: 5 });
        console.error("无法加载JSONL数据");
      },
    });
  }

  // 监听搜索事件
  form.on("submit(doSearch)", function (data) {
    loadData(data.field);
    return false; // 阻止表单跳转
  });
  form.on("submit(refresh)", function (data) {
    getFileList();
    return false; // 阻止表单跳转
  });

  // 监听工具条事件
  table.on("tool(test)", function (obj) {
    var data = obj.data; // 获取当前行数据
    if (obj.event === "detail") {
      // 将\n替换为<br>以在HTML中正确显示换行
      //数组转字符串
      data["premises"] = data["premises"].join("<br><hr>");
      data["premises-FOL"] = data["premises-FOL"].join("<br><hr>");
      data["response"] = data["response"].join("<br><hr>");
      var details = `<div class="">
      ${data.id}
<div class="layui-row">
<!-- 自然语言 -->
<div class="layui-col-xs4 layui-col-sm4 layui-col-m4">
  <table class="layui-table" border="1">
    <tr>
      <th>自然语言</th>
    </tr>
    ${data["premises"]
      .split("<br><hr>")
      .map((item) => `<tr><td>${item}</td></tr>`)
      .join("")}
  </table>
</div>

<div class="layui-col-xs4 layui-col-sm4 layui-col-m4">
<table class="layui-table" border="1">
<tr>
<th>标注参考</th>
</tr>
<tr>
<td>${data["premises-FOL"]}</td>
</tr>
</table>
</div>
<!-- GPT输出 -->
<div class="layui-col-xs4 layui-col-sm4 layui-col-m4">
  <table class="layui-table" border="1">
    <tr>
      <th>GPT输出</th>
    </tr>
    ${data["response"]
      .split("<br><hr>")
      .map((item) => `<tr><td>${item}</td></tr>`)
      .join("")}
  </table>
</div>
</div>
<table class="layui-table" border="1">
<tr>
<th>结论</th>
<th>参考结论</th>
<th>结论-FOL（GPT）</th>
</tr>
<tr>
<td>${data["conclusion"]}</td>
<td>${data["conclusion-FOL"]} <br>${data["label"]}</td>
<td>${data["conclusion-AI"]} <br>${data["label-AI"]}</td>
</tr>
</table>
<table class="layui-table" border="1">
<tr>
<th>常量</th>
<th>谓词</th>
<th>错误日志</th>
</tr>
<tr>
<td>${data["constants-AI"].replace(/\n/g, "<br>")}</td>
<td>${data["predicates-AI"].replace(/\n/g, "<br>")}</td>
<td>${data["errmsg"].replace(/\n/g, "<br>")}</td>
</tr>
</table>
</div>
`;

      // <!-- 其他表格可以继续放在这里，它们将显示在下一行 -->
      //   <table class="layui-table" border="1">
      //     <tr>
      //       <th>常量</th>
      //       <th>谓词</th>
      //     </tr>
      //     <tr>
      //       <td>${data["FOL_Analysis"]["constants"]}</td>
      //       <td>${JSON.stringify(data["FOL_Analysis"]["predicates"])}</td>
      //     </tr>
      //   </table>
      // <table class="layui-table" border="1">
      //   <tr>
      //     <th>提示</th>
      //   </tr>
      //   <tr>
      //     <td>${marked.parse(data["prompt"])}</td>
      //   </tr>
      // </table>
      // </div>
      index = layer.open({
        title: "详细信息",
        content: details,
        shadeClose: true, //点击遮罩关闭层
        maxmin: true,
        area: ["85%", "85%"],
      });
      // 设置弹层最大化
      layer.full(index);
    }
  });
});
