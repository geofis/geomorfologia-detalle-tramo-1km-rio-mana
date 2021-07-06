<!DOCTYPE qgis PUBLIC 'http://mrcc.com/qgis.dtd' 'SYSTEM'>
<qgis styleCategories="AllStyleCategories" maxScale="0" minScale="1e+8" hasScaleBasedVisibilityFlag="0" version="3.12.0-București">
  <flags>
    <Identifiable>1</Identifiable>
    <Removable>1</Removable>
    <Searchable>0</Searchable>
  </flags>
  <customproperties>
    <property key="WMSBackgroundLayer" value="false"/>
    <property key="WMSPublishDataSourceUrl" value="false"/>
    <property key="embeddedWidgets/count" value="0"/>
    <property key="identify/format" value="Value"/>
  </customproperties>
  <pipe>
    <rasterrenderer type="paletted" alphaBand="-1" nodataColor="" band="1" opacity="1">
      <rasterTransparency/>
      <minMaxOrigin>
        <limits>None</limits>
        <extent>WholeRaster</extent>
        <statAccuracy>Estimated</statAccuracy>
        <cumulativeCutLower>0.02</cumulativeCutLower>
        <cumulativeCutUpper>0.98</cumulativeCutUpper>
        <stdDevFactor>2</stdDevFactor>
      </minMaxOrigin>
      <colorPalette>
        <paletteEntry color="#000000" value="0" alpha="255" label="unlabeled"/>
        <paletteEntry color="#ffab4b" value="1" alpha="255" label="clasts"/>
        <paletteEntry color="#d8d8d8" value="2" alpha="255" label="riffle-shallow-glare"/>
        <paletteEntry color="#8dffa6" value="3" alpha="255" label="low-vegetation"/>
        <paletteEntry color="#003ffe" value="4" alpha="255" label="pool"/>
        <paletteEntry color="#006617" value="5" alpha="255" label="riparian-vegetation"/>
        <paletteEntry color="#ffffff" value="6" alpha="0" label="background"/>
        <paletteEntry color="#ffd641" value="7" alpha="255" label="bar"/>
        <paletteEntry color="#525252" value="8" alpha="255" label="shadow"/>
      </colorPalette>
      <colorramp name="[source]" type="randomcolors"/>
    </rasterrenderer>
    <brightnesscontrast contrast="0" brightness="0"/>
    <huesaturation colorizeOn="0" colorizeGreen="128" colorizeRed="255" colorizeBlue="128" colorizeStrength="100" grayscaleMode="0" saturation="0"/>
    <rasterresampler maxOversampling="2"/>
  </pipe>
  <blendMode>0</blendMode>
</qgis>
