import GeoRasterLayer from "georaster-layer-for-leaflet";


export function renderGeoraster({ georaster, chart_data }) {
if(process.env.DEV) console.log("renderGeoraster==================== ", chart_data);
  let layer = new GeoRasterLayer({
    debugLevel: 0,
    georaster: georaster,
    opacity: 1,
    pixelValuesToColorFn: function (values) {
      if (values[0] === georaster.noDataValue) {
        return null;
      }

      if (chart_data.indicator === "forest_fire") {
        if (values[0] >= -500 && values[0] <= -101) return "#768833";
        // if(values[0] >=-250 && values[0]<=-101) return "#a8bf54"
        if (values[0] >= -100 && values[0] <= 99) return "#0ce244";
        if (values[0] >= 100 && values[0] <= 269) return "#f5fe0c";
        // if(values[0] >=270 && values[0]<=439) return "#f8b040"
        if (values[0] >= 270 && values[0] <= 659) return "#fa671a";
        if (values[0] >= 660 && values[0] <= 1300) return "#a500d2";
      }
      if (chart_data.indicator === "forest_fire_risk") {
        if (values[0] > 273) return "red"
        // if(values[0] === 0) return "red"
      }
      else {
        const color = chart_data.raster_colors.find(item => {
          return item.val === values[0]
        })
        return color?.color || "blue";
      }
    },
    resolution: 64 // optional parameter for adjusting display resolution
  });

  return layer;
}
