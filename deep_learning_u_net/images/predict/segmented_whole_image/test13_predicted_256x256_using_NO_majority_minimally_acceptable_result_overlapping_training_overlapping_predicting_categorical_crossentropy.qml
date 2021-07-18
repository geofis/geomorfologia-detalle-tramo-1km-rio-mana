<!DOCTYPE qgis PUBLIC 'http://mrcc.com/qgis.dtd' 'SYSTEM'>
<qgis version="3.12.0-București" maxScale="0" minScale="1e+8" hasScaleBasedVisibilityFlag="0" styleCategories="AllStyleCategories">
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
    <rasterrenderer opacity="1" nodataColor="" alphaBand="-1" band="1" type="paletted">
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
        <paletteEntry label="background" color="#ffffff" alpha="0" value="0"/>
        <paletteEntry label="clasts" color="#ffab4b" alpha="255" value="1"/>
        <paletteEntry label="riffle-shallow-glare" color="#d8d8d8" alpha="255" value="2"/>
        <paletteEntry label="low-vegetation" color="#8dffa6" alpha="255" value="3"/>
        <paletteEntry label="pool" color="#003ffe" alpha="255" value="4"/>
        <paletteEntry label="riparian-vegetation" color="#006617" alpha="255" value="5"/>
        <paletteEntry label="bar" color="#ffd641" alpha="255" value="6"/>
        <paletteEntry label="shadow" color="#525252" alpha="255" value="7"/>
      </colorPalette>
      <colorramp name="[source]" type="randomcolors"/>
    </rasterrenderer>
    <brightnesscontrast contrast="0" brightness="0"/>
    <huesaturation colorizeBlue="128" saturation="0" colorizeStrength="100" colorizeGreen="128" grayscaleMode="0" colorizeOn="0" colorizeRed="255"/>
    <rasterresampler maxOversampling="2"/>
  </pipe>
  <blendMode>0</blendMode>
</qgis>
