<!DOCTYPE qgis PUBLIC 'http://mrcc.com/qgis.dtd' 'SYSTEM'>
<qgis styleCategories="AllStyleCategories" hasScaleBasedVisibilityFlag="0" version="3.12.0-București" maxScale="0" minScale="1e+8">
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
    <rasterrenderer type="paletted" nodataColor="" alphaBand="-1" band="1" opacity="1">
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
        <paletteEntry label="unlabeled" alpha="255" color="#000000" value="0"/>
        <paletteEntry label="clasts" alpha="255" color="#ffab4b" value="1"/>
        <paletteEntry label="riffle-shallow-glare" alpha="255" color="#d8d8d8" value="2"/>
        <paletteEntry label="low-vegetation" alpha="255" color="#8dffa6" value="3"/>
        <paletteEntry label="pool" alpha="255" color="#003ffe" value="4"/>
        <paletteEntry label="riparian-vegetation" alpha="255" color="#006617" value="5"/>
        <paletteEntry label="background" alpha="0" color="#ffffff" value="6"/>
        <paletteEntry label="bar" alpha="255" color="#ffd641" value="7"/>
        <paletteEntry label="shadow" alpha="255" color="#525252" value="8"/>
      </colorPalette>
      <colorramp type="randomcolors" name="[source]"/>
    </rasterrenderer>
    <brightnesscontrast brightness="0" contrast="0"/>
    <huesaturation colorizeBlue="128" colorizeOn="0" grayscaleMode="0" colorizeRed="255" colorizeStrength="100" saturation="0" colorizeGreen="128"/>
    <rasterresampler maxOversampling="2"/>
  </pipe>
  <blendMode>0</blendMode>
</qgis>
