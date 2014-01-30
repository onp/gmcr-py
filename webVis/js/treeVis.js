(function (treeVis, $, undefined) {
    "use strict";

    treeVis.name = "Tree";
    treeVis.treeDepth = 3;
    treeVis.showOnlyUIs = false;
    var tree = d3.layout.tree();
    var rootNode, treeRoot, conflict, container;
    var visNodes, visLinks, visLabels;  // d3 selections
    var nodeData, linkData;  // d3 tree generated data arrays

    var buildTree = function (sourceNode, dm, height) {
        //recursively builds a tree of the requested height from the given source node.
        //dm specifies the decision maker who made the move to this node, and so
        //  cannot move again immediately.
        var thisNode = {};
        thisNode.dat = sourceNode;
        thisNode.height = height;
        thisNode.dm = dm;
        if (height > 0) {
            thisNode.children = $.map(sourceNode.reachable, function (a) {
                if (treeVis.showOnlyUIs && (a.payoffChange < 1)){
                    //don't add the node.
                } else if (a.dm !== dm) {
                    return buildTree(a.target, a.dm, height-1);
                }
            });
        } else {
            thisNode.children = [];
        }
        return thisNode;
    };

    var diagonal = d3.svg.diagonal()        //used in making lines in the tree layout.
        .projection(function (d) {return [d.x, d.y+20]; });

    var refresh = function () {
        d3.selectAll("circle").style("fill", "lightBlue")
        treeRoot = buildTree(rootNode, null, treeVis.treeDepth);

        nodeData = tree.nodes(treeRoot);    //insert structure into d3 tree
        linkData = tree.links(nodeData);    //store calculated link data

        visNodes = container.selectAll(".node").data(nodeData);    //establish d3 selection variables
        visLinks = container.selectAll(".link").data(linkData);
        visLabels = container.selectAll(".label").data(nodeData);
    
        visLinks.exit().remove();
        visLinks.enter().insert("path", "circle");
        visLinks.attr("d", diagonal)
            .attr("class", function (d) {return "link " + d.target.dm; });

        visNodes.exit().remove();
        visNodes.enter().insert("circle", "text")
            .attr("r", 10)
            .on("mouseover", function () {
                d3.selectAll("circle." + this.classList[1])
                    .style("fill", "paleVioletRed");
                d3.select(this)
                    .style("stroke-width", "2px");
            })
            .on("mouseout", function () {
                d3.selectAll("circle." + this.classList[1])
                    .style("stroke-width", "1.5px")
                    .style("fill", "lightBlue");
            })
            .on("click", function (d) {
                d3.selectAll("circle." + this.classList[1])
                    .style("fill", "lightBlue");
                treeVis.changeRoot(d.dat.id);
            });

        visNodes.attr("class", function (d) {return "node st" + d.dat.id; })
            .attr("cx", function (d) {return d.x; })
            .attr("cy", function (d) {return d.y + 20; });

        visLabels.exit().remove();
        visLabels.enter()
            .append("text")
            .attr("class", "label")
            .attr("dy", 3);
        visLabels.text(function (d) {return d.dat.ordered; })
            .attr("transform", function (d) {
                return "translate(" + (d.x) + "," + (d.y + 20) + ")";
            });

    };

    treeVis.loadVis = function (newConflict, newContainer) {
        //Loads the visualization into the container.
        conflict = newConflict;
        container = newContainer;
        rootNode = conflict.data.nodes[0];
        treeVis.resize();
    };
    
    treeVis.clearVis = function () {
        visLabels.data([]).exit().remove()
        visLinks.data([]).exit().remove()
        visNodes.data([]).exit().remove()
    }
    
    treeVis.changeRoot = function (newRoot){
        rootNode = conflict.data.nodes[newRoot];
        refresh();
    }
    
    treeVis.refresh = refresh;
    
    treeVis.resize = function () {
        tree.size([container.style("width").slice(0, -2), container.style("height").slice(0, -2) - 100]);
        refresh();
    }
    
    treeVis.visConfig = function(){
        var config = $(
            "<li>                                               \
                <select name='treeDepth' id='treeDepth'>        \
                    <option value=2>2</option>                  \
                    <option value=3>3</option>                  \
                    <option value=4>4</option>                  \
                    <option value=5>5</option>                  \
                    <option value=6>6</option>                  \
                </select>                                       \
                <label for='treeDepth'>Tree Depth</label>       \
            </li>                                               \
            <li>                                                \
                <input type='checkbox' name='ui' id='ui'>       \
                <label for='ui'>Only show UIs</label>           \
            </li>");
            
        config.find("#treeDepth")
            .val(treeVis.treeDepth)
            .change(function(){
                treeVis.treeDepth = $(this).val();
                refresh();
            });
        config.find("#ui")
            .prop("checked", treeVis.showOnlyUIs)
            .change(function(){
                treeVis.showOnlyUIs = $(this).prop("checked");
                refresh();
            });
        
        $("ul#vis-config").html('').append(config);
    
    };


}(window.treeVis = window.treeVis || {}, jQuery));