;(function($scope, $) {
 
    $.extend($scope, {
    
        init: function() {
            $scope.viewer = new Cesium.Viewer('cesiumContainer', {
                baseLayerPicker: false,
                terrainProvider: new Cesium.CesiumTerrainProvider({
                url: '//assets.agi.com/stk-terrain/world'
                })
            });
            
            $scope.entity = $scope.viewer.entities.add({
                id: "Main",
                wall: {
                    positions: [],
                    material: Cesium.Color.fromHsl(0.0, 1, 1, 0.2),
                    outline: true,
                    outlineColor: Cesium.Color.BLUE,
                    outlineWidth: 2
                }
            });
            
            /*
            $scope.viewer.entities.add({
                position : Cesium.Cartesian3.fromDegrees(-75.59777, 40.03883),
                billboard :{
                    image : '/img/logo.png'
                }
            });*/
        },
        
        addPositions: function(positions) {
            $scope.positions = $.map(positions, function (item) { //TODO: concat
                return $scope.convertPosition(item);
            });
            
            $scope.render();
        },
        
        addPosition: function (position) {
            $scope.positions.push($scope.convertPosition(position));
            
            $scope.render();
        },
        
        convertPosition: function(position) {
            return $.extend(Cesium.Cartesian3.fromDegrees(position.lat, position.lon, position.alt), position);
        },
        
        render: function() {
            $scope.entity.wall.positions._value = $scope.positions;
            $scope.entity.wall.positions.definitionChanged.raiseEvent();
        }
    
    });
 
}(window.space = window.space || {}, jQuery));