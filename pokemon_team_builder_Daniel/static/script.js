let team = Array(6).fill(null);

let pokemonTypes = {};

// Load pokedex.json from the URL and parse the type information
$.getJSON(
  "https://play.pokemonshowdown.com/data/pokedex.json",
  function (data) {
    Object.keys(data).forEach((pokemonName) => {
      pokemonTypes[pokemonName.replace(/\s+/g, "").toLowerCase()] =
        data[pokemonName].types;
    });
  }
);

function getTypeColor(pokemonName) {
  const types = pokemonTypes[pokemonName.replace(/\s+/g, "").toLowerCase()];
  if (!types) {
    return "#FFFFFF"; // Default to white if type not found
  }

  if (types.length === 1) {
    const color1 = typeColors[types[0]] || "#FFFFFF";
    return `color: ${color1};`;
  } else if (types.length === 2) {
    const color1 = typeColors[types[0]] || "#FFFFFF";
    const color2 = typeColors[types[1]] || "#FFFFFF";
    return `background: -webkit-linear-gradient(45deg, ${color1} 40%, ${color2} 60%); -webkit-background-clip:text; -webkit-text-fill-color: transparent`;
  }

  return "#FFFFFF";
}

function createRandomString(length) {
  const chars = "abcdefghijklmnopqrstuvwxyz";
  let result = "";
  for (let i = 0; i < length; i++) {
    result += chars.charAt(Math.floor(Math.random() * chars.length));
  }
  return result;
}

function updateTeamDisplay() {
  $("#team-container").empty();

  const statColors = {
    HP: "#FF6347",
    Atk: "#F08030",
    Def: "#FFD531",
    SpA: "#6790EF",
    SpD: "#7CCE52",
    Spe: "#F25685",
  };

  team.forEach((pokemon, index) => {
    if (pokemon) {
      let spreadDisplay = Object.entries(pokemon.evs)
        .map(([stat, value]) =>
          value != 0
            ? `<span style="color: ${statColors[stat]}">${value} ${stat}</span>`
            : ""
        )
        .filter(Boolean)
        .join("<br>");

      $("#team-container").append(`
                <article class="pokemon-slot" data-slot="${index}">
                    <div class="pokemon-info">
                        <div class="img">
                            <img class="img-pokemon" src="https://play.pokemonshowdown.com/sprites/gen5/${pokemon.name
                              .replace(" ", "")
                              .toLowerCase()}.png" alt="${pokemon.name}">
                            <img class="img-item" src="https://www.serebii.net/itemdex/sprites/sv/${
                              pokemon.item.replace(" ", "").toLowerCase() || ""
                            }.png" alt="No Item">
                            <button class="button item" data-type="item" data-slot="${index}">Item:<br> ${
        pokemon.item || ""
      }</button>
                        </div>
                        <div class="details">
                            <span class="name" style="${getTypeColor(pokemon.name)};">${pokemon.name}</span>
                            <button class="button ability" data-type="ability" data-slot="${index}">Ability: ${
        pokemon.ability || ""
      }</button>
                            <button class="button spread" data-type="spread" data-slot="${index}">EV Spread:<br>${
        spreadDisplay || ""
      }</button>
                            <div class="moves-grid">
                                ${pokemon.moves
                                  .map(
                                    (move, i) => `
                                    <button class="move-button" data-type="move" data-slot="${index}" data-move-index="${i}" style="color: ${getMoveTypeColor(
                                      move
                                    )}">${move || "---"}</button>
                                `
                                  )
                                  .join("")}
                            </div>
                        </div>
                    </div>
                </article>
            `);
    } else {
      $("#team-container").append(`
                <article class="empty-slot" data-slot="${index}">
                    <div class="pokemon-info">
                        <div class="img">
                            <img class="img-pokemon" src="https://img.pokemondb.net/sprites/black-white/normal/unown-${createRandomString(
                              1
                            )}.png" alt="Empty Slot">
                        </div>
                        <div class="details">
                            <span class="name">Empty Slot</span>
                        </div>
                    </div>
                </article>
            `);
    }
  });

  // Attach event listeners for the move buttons
  $(".move-button").on("click", function () {
    const slotIndex = $(this).data("slot");
    const moveIndex = $(this).data("move-index");
    showMoves(slotIndex, moveIndex);
  });
}

function getSuggestions() {
  $.ajax({
    url: "/suggest",
    method: "POST",
    contentType: "application/json",
    data: JSON.stringify({ team: team.filter((pokemon) => pokemon !== null) }),
    success: function (data) {
      $("#suggestions-list").empty();
      data.suggestions.forEach((pokemon, index) => {
        const probability = data.probabilities[index];
        $("#suggestions-list").append(`
                    <li>
                        <img src="https://play.pokemonshowdown.com/sprites/gen5/${pokemon.name
                          .replace(" ", "")
                          .toLowerCase()}.png" alt="${
          pokemon.name
        }" style="width: 60px; height: 60px; margin-right: 10px;">
                        <span>${
                          pokemon.name
                        }</span><span style="color:#71A7FF; padding-left: 20px;">(${(
          probability * 100
        ).toFixed(4)}%)</span>
                        <button class="suggestion-btn" data-pokemon='${JSON.stringify(
                          pokemon
                        )}' style="display:none;"></button>
                    </li>
                    <hr class="divider"/>
                `);
      });
      $("#suggestions-container").show();
      $("#suggestions-list li").on("click", function () {
        const pokemon = JSON.parse(
          $(this).find(".suggestion-btn").attr("data-pokemon")
        );
        const slotIndex = $("#suggestions-container").data("slotIndex");
        team[slotIndex] = pokemon;
        updateTeamDisplay();
        $("#suggestions-container").hide();
      });
    },
  });
}

$(document).on("click", ".empty-slot", function () {
  const slotIndex = $(this).data("slot");
  $("#suggestions-container").data("slotIndex", slotIndex);
  getSuggestions();
});

$("#search-pokemon").on("input", function () {
  const searchTerm = $(this).val().toLowerCase();
  $("#suggestions-list li").each(function () {
    const listItem = $(this);
    const divider = listItem.next("hr.divider");
    const pokemonName = listItem.find("span").first().text().toLowerCase();

    if (pokemonName.includes(searchTerm)) {
      listItem.show();
      divider.show();
    } else {
      listItem.hide();
      divider.hide();
    }
  });
});

$("#search-pokemon").on("keypress", function (e) {
  if (e.which == 13) {
    // Enter key pressed
    const pokemonName = $(this).val().trim();
    if (pokemonName) {
      const newPokemon = {
        name: pokemonName,
        ability: "",
        item: "",
        moves: ["", "", "", ""],
        nature: "",
        evs: { HP: 0, Atk: 0, Def: 0, SpA: 0, SpD: 0, Spe: 0 },
        teraType: "",
        lead: false,
      };
      const slotIndex = $("#suggestions-container").data("slotIndex");
      team[slotIndex] = newPokemon;
      updateTeamDisplay();
      $("#suggestions-container").hide();
    }
  }
});

$("#close-suggestions").on("click", function () {
  $("#suggestions-container").hide();
});

$(document).on("click", ".button", function () {
  const slotIndex = $(this).data("slot");
  const type = $(this).data("type");
  if (type === "ability") {
    showAbilities(slotIndex);
  } else if (type === "item") {
    showItems(slotIndex);
  } else if (type === "moves") {
    showMoves(slotIndex);
  } else if (type === "spread") {
    showSpreads(slotIndex);
  }
});

function showAbilities(slotIndex) {
  const pokemon = team[slotIndex];
  $("#abilities-list").empty();

  $.ajax({
    url: "/suggest_ability",
    method: "POST",
    contentType: "application/json",
    data: JSON.stringify({
      team: team.filter((pokemon) => pokemon !== null),
      pokemon: pokemon,
    }),
    success: function (data) {
      const abilities = data.suggestions;
      const probabilities = data.probabilities;

      abilities.forEach((ability, index) => {
        const probability = probabilities[index];
        $("#abilities-list").append(`
                    <li>
                        <span>${ability} (${(probability * 100).toFixed(
          2
        )}%)</span>
                        <button class="ability-btn" data-ability="${ability}" style="display:none;"></button>
                    </li>
                    <hr class="divider"/>
                `);
      });

      $("#abilities-container").show();
      $("#abilities-list li").on("click", function () {
        const ability = $(this).find(".ability-btn").attr("data-ability");
        pokemon.ability = ability;
        $(`button[data-slot="${slotIndex}"][data-type="ability"]`).text(
          `Ability: ${ability}`
        );
        updateTeamDisplay();
        $("#abilities-container").hide();
      });
    },
  });
}

$("#close-abilities").on("click", function () {
  $("#abilities-container").hide();
});

function showItems(slotIndex) {
  const pokemon = team[slotIndex];
  $("#items-list").empty();

  $.ajax({
    url: "/suggest_item",
    method: "POST",
    contentType: "application/json",
    data: JSON.stringify({
      team: team.filter((pokemon) => pokemon !== null),
      pokemon: pokemon,
    }),
    success: function (data) {
      const items = data.suggestions;
      const probabilities = data.probabilities;

      items.forEach((item, index) => {
        const probability = probabilities[index];
        $("#items-list").append(`
                    <li>
                        <img src="https://www.serebii.net/itemdex/sprites/sv/${item
                          .replace(" ", "")
                          .toLowerCase()}.png" alt="${item}" style="width: 20px; height: 20px; margin-right: 10px;">
                        <span>${item} (${(probability * 100).toFixed(
          2
        )}%)</span>
                        <button class="item-btn" data-item="${item}" style="display:none;"></button>
                    </li>
                    <hr class="divider"/>
                `);
      });

      $("#items-container").show();
      $("#items-list li").on("click", function () {
        const item = $(this).find(".item-btn").attr("data-item");
        pokemon.item = item;
        $(`button[data-slot="${slotIndex}"][data-type="item"]`).text(
          `Item: ${item}`
        );
        updateTeamDisplay();
        $("#items-container").hide();
      });
    },
  });
}

$("#close-items").on("click", function () {
  $("#items-container").hide();
});

let moveTypes = {};

// Load moves.json from the URL and parse the move types
$.getJSON("https://play.pokemonshowdown.com/data/moves.json", function (data) {
  Object.keys(data).forEach((moveName) => {
    moveTypes[moveName.replace(/\s+/g, "").toLowerCase()] = data[moveName].type;
  });
});

const typeColors = {
  Fire: "#FF4422",
  Water: "#3399FF",
  Grass: "#77CC55",
  Electric: "#FFCC33",
  Ice: "#66CCFF",
  Fighting: "#BB5544",
  Poison: "#AA5599",
  Ground: "#DDBB55",
  Flying: "#8899FF",
  Psychic: "#FF5599",
  Bug: "#AABB22",
  Rock: "#BBAA66",
  Ghost: "#6666BB",
  Dragon: "#7766FE",
  Dark: "#775544",
  Steel: "#AAAABB",
  Fairy: "#EE99EE",
  Normal: "#AAAA99",
};

function getMoveTypeColor(moveName) {
  const moveType = moveTypes[moveName.replace(/\s+/g, "").toLowerCase()];
  return typeColors[moveType] || "#FFFFFF"; // Default to white if type not found
}

// Update the showMoves function to apply move colors
function showMoves(slotIndex, moveIndex) {
  const pokemon = team[slotIndex];
  $("#moves-list").empty();

  $.ajax({
    url: "/suggest_move",
    method: "POST",
    contentType: "application/json",
    data: JSON.stringify({
      team: team.filter((pokemon) => pokemon !== null),
      pokemon: pokemon,
    }),
    success: function (data) {
      const moves = data.suggestions;
      const probabilities = data.probabilities;
      const selectedMoves = new Set(pokemon.moves.filter((move) => move));

      moves.forEach((move, index) => {
        const probability = probabilities[index];
        if (!selectedMoves.has(move)) {
          $("#moves-list").append(`
                        <li>
                            <div class="individualsinmovelist">
                                <span style="color:${getMoveTypeColor(
                                  move
                                )}">${move}</span> <span style="color:#71A7FF; padding-left: 10px;"> (${(
            probability * 100
          ).toFixed(2)}%)</span>
                                <button class="move-btn" data-move='${JSON.stringify(
                                  move
                                )}' style="display:none;"></button>
                            </div>
                        </li>
                        <hr class="divider"/>
                    `);
        }
      });

      $("#moves-container").show();
      $("#moves-list li").on("click", function () {
        const move = JSON.parse($(this).find(".move-btn").attr("data-move"));
        pokemon.moves[moveIndex] = move;
        updateTeamDisplay();
        $("#moves-container").hide();
      });
    },
  });
}

function showSpreads(slotIndex) {
  const pokemon = team[slotIndex];
  $("#spreads-list").empty();

  const statColors = {
    HP: "#FF6347",
    Atk: "#F08030",
    Def: "#FFD531",
    SpA: "#6790EF",
    SpD: "#7CCE52",
    Spe: "#F25685",
  };

  $.ajax({
    url: "/suggest_spread",
    method: "POST",
    contentType: "application/json",
    data: JSON.stringify({
      team: team.filter((pokemon) => pokemon !== null),
      pokemon: pokemon,
    }),
    success: function (data) {
      const spreads = data.suggestions;
      const probabilities = data.probabilities;

      spreads.forEach((spread, index) => {
        const probability = probabilities[index];
        const [nature, evs] = parseSpread(spread);
        let evsDisplay = "";

        Object.entries(evs).forEach(([stat, value]) => {
          if (value != 0) {
            evsDisplay += `<span style="color: ${statColors[stat]}; margin-right: 5px; margin-left: 5px;">${value} ${stat}</span>`;
          }
        });

        $("#spreads-list").append(`
                    <li>
                        <span style="margin-right: 5px;">${nature} </span><br>
                        ${evsDisplay}
                        <span style="color:#71A7FF;">(${(
                          probability * 100
                        ).toFixed(2)}%)</span>
                        <button class="spread-btn" data-spread="${spread}" style="display:none;"></button>
                    </li>
                    <hr class="divider"/>
                `);
      });

      $("#spreads-container").show();
      $("#spreads-list li").on("click", function () {
        const spread = $(this).find(".spread-btn").attr("data-spread");
        const [nature, evs] = parseSpread(spread);
        pokemon.nature = nature;
        pokemon.evs = evs;
        const natureText = Object.entries(nature);
        const spreadText = Object.entries(evs)
          .map(([stat, value]) => (value != 0 ? `${value} ${stat}` : ""))
          .filter(Boolean)
          .join(" / ");
        $(`button[data-slot="${slotIndex}"][data-type="spread"]`).html(
          `EV Spread:${natureText}<br>${spreadText}`
        );
        updateTeamDisplay();
        $("#spreads-container").hide();
      });
    },
  });
}

$("#close-spreads").on("click", function () {
  $("#spreads-container").hide();
});

function parseSpread(spread) {
  const [nature, evString] = spread.split(":");
  const evValues = evString.split("/").map(Number);
  const evs = {
    HP: evValues[0],
    Atk: evValues[1],
    Def: evValues[2],
    SpA: evValues[3],
    SpD: evValues[4],
    Spe: evValues[5],
  };
  return [nature, evs];
}

function generateTeamText() {
    return team
      .map((pokemon) => {
        if (!pokemon) return '';
  
        const evs = Object.entries(pokemon.evs)
          .filter(([stat, value]) => value != 0)
          .map(([stat, value]) => `${value} ${stat}`)
          .join(' / ');
  
        const moves = pokemon.moves.map((move) => `- ${move}`).join('\n');
  
        return `${pokemon.name} @ ${pokemon.item}\nAbility: ${pokemon.ability}\nTera Type: ${pokemon.teraType}\nEVs: ${evs}\n${pokemon.nature} Nature\nIVs: ${pokemon.ivs || ''}\n${moves}`;
      })
      .filter(Boolean)
      .join('\n\n');
}

function copyToClipboard(text) {
    const tempInput = document.createElement('textarea');
    tempInput.value = text;
    document.body.appendChild(tempInput);
    tempInput.select();
    document.execCommand('copy');
    document.body.removeChild(tempInput);
}
  


$(document).ready(function () {
  updateTeamDisplay();

  $('#copy-team-btn').on('click', function () {
    const teamText = generateTeamText();
    copyToClipboard(teamText);
    alert('Team copied to clipboard!');
  });



  // Other event listeners...
});
