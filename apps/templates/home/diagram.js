var viewer = new drawio.Viewer(document.getElementById('drawio'));

var xmlData = `<mxfile>
  <diagram name="Flowchart" user="none">
    <mxGraphModel>
      <root>
        <mxCell id="0" />
        <mxCell id="1" parent="0" />
        <mxCell id="2" value="Start" style="ellipse" vertex="1" connectable="0" parent="1">
          <mxGeometry x="40" y="40" width="80" height="40" as="geometry" />
        </mxCell>
        <mxCell id="3" value="End" style="ellipse" vertex="1" connectable="0" parent="1">
          <mxGeometry x="240" y="240" width="80" height="40" as="geometry" />
        </mxCell>
        <mxCell id="4" value="Decision" style="rhombus" vertex="1" connectable="0" parent="1">
          <mxGeometry x="140" y="140" width="80" height="80" as="geometry" />
        </mxCell>
        <mxCell id="5" style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;" edge="1" parent="1" source="2" target="4">
          <mxGeometry relative="1" as="geometry" />
        </mxCell>
        <mxCell id="6" style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;" edge="1" parent="1" source="4" target="3">
          <mxGeometry relative="1" as="geometry" />
        </mxCell>
      </root>
    </mxGraphModel>
  </diagram>
</mxfile>`;

viewer.displayXml(xmlData);
