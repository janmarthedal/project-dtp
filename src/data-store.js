import Sequelize from 'sequelize';

function defineMathItem(sequelize) {
    const MathItem = sequelize.define('mathitem', {
        id: {
            type: Sequelize.INTEGER,
            primaryKey: true,
            autoIncrement: true
        },
        item_type: {
            type: Sequelize.CHAR(1),
            allowNull: false
        },
        body: {
            type: Sequelize.TEXT,
            allowNull: false
        },
    }, {
        timestamps: true,
        updatedAt: false,
        underscored: true
    });
    MathItem.belongsTo(MathItem, {as: 'parent'});
    return MathItem;
}

function defineDraftItem(sequelize, MathItem) {
    const DraftItem = sequelize.define('draftitem', {
        id: {
            type: Sequelize.INTEGER,
            primaryKey: true,
            autoIncrement: true
        },
        item_type: {
            type: Sequelize.CHAR(1),
            allowNull: false
        },
        notes: {
            type: Sequelize.TEXT,
            allowNull: false
        },
        body: {
            type: Sequelize.TEXT,
            allowNull: false
        },
    }, {
        timestamps: true,
        underscored: true
    });
    DraftItem.belongsTo(MathItem, {as: 'parent'});
    return DraftItem;
}

class DataStore {
    constructor() {
        let sequelize = new Sequelize('teoremer', null, null, {
          dialect: 'sqlite',
          storage: './db.sqlite'
        });
        this.MathItem = defineMathItem(sequelize);
        this.DraftItem = defineDraftItem(sequelize, this.MathItem);
    }
    init() {
        console.log('Initializing data store');
        return Promise.all([
            this.MathItem.sync(),
            this.DraftItem.sync(),
        ]);
    }
    create_draft(item_type, body, notes) {
        return this.DraftItem.create({item_type, body, notes}).then(item => item.id);
    }
    update_draft(id, body, notes) {
        return this.DraftItem.findById(id).then(item => item.update({body, notes}));
    }
    delete_draft(id) {
        return this.DraftItem.findById(id).then(item => item.destroy());
    }
    get_draft(id) {
        return this.DraftItem.findById(id);
    }
    get_draft_list() {
        return this.DraftItem.findAll({
            attributes: ['id', 'item_type', 'notes', 'updated_at']
        });
    }
    create_mathitem(item_type, body) {
        return this.MathItem.create({item_type, body}).then(item => item.id);
    }
    get_mathitem(id) {
        return this.MathItem.findById(id);
    }
    get_mathitem_list() {
        return this.MathItem.findAll({
            attributes: ['id', 'item_type', 'created_at']
        });
    }
}

const datastore = new DataStore();

export const DEFINITION = 'D';
export const THEOREM = 'T';
export const PROOF = 'P';
export const datastore_ready = datastore.init().then(() => datastore);