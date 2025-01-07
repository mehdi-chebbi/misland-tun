import { reactive } from "vue";

export default {
  dataProcessor: ({ results, indicator }) => {
    if (process.env.DEV) console.log(indicator, " -------------- indicator in stats --------------", results.stats.mapping);
    // const labels = results.stats.stats[0].stats.map(stat => stat.label)
    const labels = results.stats.stats[0].stats.map(stat => stat.label)
    console.log("///////////////////////////////////////////////////////////////////////")
    console.log(results)
    console.log("///////////////////////////////////////////////////////////////////////")
    const colors_init = results.stats.mapping.map(stat => stat.color);
    const backgroundColor = new Array(labels.length).fill(null)
    const values = results.stats.stats[0].stats.map(stat => (stat.value / 10000).toFixed(2))
    const backgroundColor_init = results.stats.stats[0].stats.map(stat => {
      let true_color = "#ffff"; // Couleur par défaut

      // Rechercher si une couleur correspond au label
      const mapping = results.stats.mapping.find(color => color.label === stat.label);

      // Si une couleur est trouvée, on l'utilise
      if (mapping) {
        true_color = mapping.color;
      }

      // Assigner la couleur dans `colors` en utilisant l'index du label
      const labelIndex = labels.indexOf(stat.label);
      if (labelIndex !== -1) {
        backgroundColor[labelIndex] = true_color;
      }

      return true_color;
    });

    console.log("*******************************************", labels)

    if (process.env.DEV) console.log("results ", { backgroundColor, labels, values });
    return {
      backgroundColor, labels, values,
      start_year: results.base,
      end_year: results.target,
    }
  },

  changeDataProcessor: ({ results, indicator }) => {
    if (process.env.DEV) console.log(indicator,"--------------- changeData processor ---------------", results);
    const labels = results.stats.map(stat => stat.label)
    const values = results.stats.map(stat => (stat.area / 10000).toFixed(2))
    // chart background colors
    const backgroundColor = results.stats.map(stat => {
      const color = indicator.colors.find(color => stat.change_type === color.change_type)
      return color?.color || "#f4f1da";
    });
    return {
      backgroundColor, labels, values, indicator
    }
  }

}
