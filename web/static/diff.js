layui.use(["form", "table", "jquery"], function () {
  var form = layui.form;
  var table = layui.table;
  var $ = layui.jquery;

  // 加载文件选项
  function loadFiles() {
    $.getJSON("/files", function (data) {
      if (data.files) {
        data.files.forEach(function (file) {
          $("#fileSelect1, #fileSelect2").append(
            '<option value="' + file + '">' + file + "</option>"
          );
        });
        form.render("select");
      }
    });
  }

  loadFiles(); // 调用加载文件

  // 处理对比
  $("#doCompare").click(function () {
    var file1 = $("#fileSelect1").val();
    var file2 = $("#fileSelect2").val();
    var filterCondition = $("#filterCondition").val();
    $.ajax({
      url: "/compare",
      type: "POST",
      contentType: "application/json",
      data: JSON.stringify({ file1: file1, file2: file2 }),
      success: function (result) {
        // 过滤数据
        var filteredData = result.filter(function (entry) {
          switch (filterCondition) {
            case "label1MatchesLabel":
              return (
                entry.item1["label-AI"] === entry.label &&
                entry.item2["label-AI"] !== entry.label
              );
            case "label2MatchesLabel":
              return (
                entry.item2["label-AI"] === entry.label &&
                entry.item1["label-AI"] !== entry.label
              );
            case "allMatch":
              return (
                entry.item1["label-AI"] === entry.label &&
                entry.item2["label-AI"] === entry.label
              );
            default:
              return true; // 无筛选
          }
        });
        var Data = filteredData.map(function (entry) {
          return {
            id: entry.id,
            labelAI1: entry.item1["label-AI"], // 访问嵌套的 label-AI 属性
            labelAI2: entry.item2["label-AI"], // 同上
            item1: entry.item1, // 顶层属性
            item2: entry.item2, // 同上
            label: entry.label, // 顶层属性
          };
        });

        // 渲染表格
        table.render({
          elem: "#compareTable",
          cols: [
            [
              { field: "id", title: "ID" },
              { field: "labelAI1", title: "标签1" },
              { field: "labelAI2", title: "标签2" },
              { field: "label", title: "标注标签" },
              { title: "操作", toolbar: "#barDemo" },
            ],
          ],
          data: Data,
        });
      },
      error: function (xhr, status, error) {
        console.error("Error: " + status + " " + error);
      },
    });
  });

  // 监听工具条事件
  table.on("tool(compareTable)", function (obj) {
    var data = obj.data; // 获取当前行数据
    if (obj.event === "detail") {
      // 将\n替换为<br>以在HTML中正确显示换行
      //数组转字符串
      //   data["premises-FOL"] = data["premises-FOL"].join("<br><hr>");
      //   data["response"] = data["response"].join("<br><hr>");
      console.log(data["item1"]);
      td = "";
      for (i in data["item1"]["premises"]) {
        td += `<tr><td>${data["item1"]["premises"][i]}</td>
        <td>${data["item1"]["premises-FOL"][i]}</td>
        <td>${data["item1"]["response"][i]}</td>
        <td>${data["item2"]["response"][i]}</td>
        </tr>`;
      }
      var details = `
<div class="layui-row">
  <table class="layui-table" border="1">
    <tr>
      <th>自然语言</th>
      <th>标注答案</th>
      <th>ai生成1</th>
      <th>ai生成2</th>
    </tr>
      ${td}
  </table>
</div>
<div class="layui-row">
结论<br>
${data["item1"]["conclusion"]}
  <table class="layui-table" border="1">
    <tr>
      <th>标注结论</th>
      <th>ai生成1</th>
      <th>ai生成2</th>
    </tr>
    <tr>
    <td>${data["item1"]["conclusion-FOL"]} <br>${data["item1"]["label"]}</td>
    <td>${data["item1"]["conclusion-AI"]} <br>${data["item1"]["label-AI"]}</td>
    <td>${data["item2"]["conclusion-AI"]} <br>${data["item2"]["label-AI"]}</td>
    </tr>
  </table>
</div>
`;
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
